/*
 * Copyright (C) 2012, Christian Halstrick <christian.halstrick@sap.com>
 * Copyright (C) 2011, Shawn O. Pearce <spearce@spearce.org> and others
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Distribution License v. 1.0 which is available at
 * https://www.eclipse.org/org/documents/edl-v10.php.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 */
package com.gerritforge.ghs.actions;

import static org.eclipse.jgit.internal.storage.pack.PackExt.BITMAP_INDEX;
import static org.eclipse.jgit.internal.storage.pack.PackExt.INDEX;
import static org.eclipse.jgit.internal.storage.pack.PackExt.PACK;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.channels.Channels;
import java.nio.channels.FileChannel;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.text.MessageFormat;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.stream.Collectors;
import org.eclipse.jgit.annotations.NonNull;
import org.eclipse.jgit.dircache.DirCacheIterator;
import org.eclipse.jgit.errors.CancelledException;
import org.eclipse.jgit.errors.CorruptObjectException;
import org.eclipse.jgit.errors.NoWorkTreeException;
import org.eclipse.jgit.internal.JGitText;
import org.eclipse.jgit.internal.storage.file.*;
import org.eclipse.jgit.internal.storage.pack.PackExt;
import org.eclipse.jgit.internal.storage.pack.PackWriter;
import org.eclipse.jgit.lib.Constants;
import org.eclipse.jgit.lib.FileMode;
import org.eclipse.jgit.lib.NullProgressMonitor;
import org.eclipse.jgit.lib.ObjectId;
import org.eclipse.jgit.lib.ObjectIdSet;
import org.eclipse.jgit.lib.ProgressMonitor;
import org.eclipse.jgit.lib.Ref;
import org.eclipse.jgit.lib.RefDatabase;
import org.eclipse.jgit.lib.ReflogEntry;
import org.eclipse.jgit.lib.ReflogReader;
import org.eclipse.jgit.revwalk.RevWalk;
import org.eclipse.jgit.storage.pack.PackConfig;
import org.eclipse.jgit.treewalk.TreeWalk;
import org.eclipse.jgit.treewalk.filter.TreeFilter;
import org.eclipse.jgit.util.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * A garbage collector for git {@link org.eclipse.jgit.internal.storage.file.FileRepository}.
 * Instances of this class are not thread-safe. Don't use the same instance from multiple threads.
 *
 * <p>Code is copied from org.eclipse.jgit.internal.storage.file.GC class
 * version: org.eclipse.jgit:6.9.0.202403050737-r sha1:e4da064611794c35cbf80a720a3f813285d5ccba</p>
 *
 */
public class BitmapGenerator {
  private static final Logger LOG = LoggerFactory.getLogger(BitmapGenerator.class);

  private final FileRepository repo;

  private ProgressMonitor pm;

  private PackConfig pconfig;

  /**
   * Creates a new garbage collector with default values. An expirationTime of two weeks and <code>
   * null</code> as progress monitor will be used.
   *
   * @param repo the repo to work on
   */
  public BitmapGenerator(FileRepository repo) {
    this.repo = repo;
    this.pconfig = new PackConfig(repo);
    this.pm = NullProgressMonitor.INSTANCE;
  }

  /**
   * Packs all objects which reachable from any of the heads into one pack file. Additionally all
   * objects which are not reachable from any head but which are reachable from any of the other
   * refs (e.g. tags), special refs (e.g. FETCH_HEAD) or index are packed into a separate pack file.
   * Objects included in pack files which have a .keep file associated are never repacked. All old
   * pack files which existed before are deleted.
   *
   * @return a collection of the newly created pack files
   * @throws java.io.IOException when during reading of refs, index, packfiles, objects,
   *     reflog-entries or during writing to the packfiles {@link java.io.IOException} occurs
   */
  public Collection<Pack> repackAndGenerateBitmap() throws IOException {

    long time = System.currentTimeMillis();
    Collection<Ref> refsBefore = getAllRefs();

    Set<ObjectId> allHeadsAndTags = new HashSet<>();
    Set<ObjectId> allHeads = new HashSet<>();
    Set<ObjectId> allTags = new HashSet<>();
    Set<ObjectId> nonHeads = new HashSet<>();
    Set<ObjectId> tagTargets = new HashSet<>();
    Set<ObjectId> indexObjects = listNonHEADIndexObjects();

    Set<ObjectId> refsToExcludeFromBitmap =
        repo.getRefDatabase().getRefsByPrefix(pconfig.getBitmapExcludedRefsPrefixes()).stream()
            .map(Ref::getObjectId)
            .collect(Collectors.toSet());

    for (Ref ref : refsBefore) {
      checkCancelled();
      nonHeads.addAll(listRefLogObjects(ref, 0));
      if (ref.isSymbolic() || ref.getObjectId() == null) {
        continue;
      }
      if (isHead(ref)) {
        allHeads.add(ref.getObjectId());
      } else if (isTag(ref)) {
        allTags.add(ref.getObjectId());
      } else {
        nonHeads.add(ref.getObjectId());
      }
      if (ref.getPeeledObjectId() != null) {
        tagTargets.add(ref.getPeeledObjectId());
      }
    }

    List<ObjectIdSet> excluded = new LinkedList<>();
    for (Pack p : repo.getObjectDatabase().getPacks()) {
      checkCancelled();
      if (!shouldPackKeptObjects() && p.shouldBeKept()) {
        excluded.add(p.getIndex());
      }
    }

    // Don't exclude tags that are also branch tips
    allTags.removeAll(allHeads);
    allHeadsAndTags.addAll(allHeads);
    allHeadsAndTags.addAll(allTags);

    // Hoist all branch tips and tags earlier in the pack file
    tagTargets.addAll(allHeadsAndTags);
    nonHeads.addAll(indexObjects);

    // Combine the GC_REST objects into the GC pack if requested
    if (pconfig.getSinglePack()) {
      allHeadsAndTags.addAll(nonHeads);
      nonHeads.clear();
    }

    List<Pack> ret = new ArrayList<>(2);
    Pack heads = null;
    if (!allHeadsAndTags.isEmpty()) {
      heads =
          writePack(
              allHeadsAndTags,
              PackWriter.NONE,
              allTags,
              refsToExcludeFromBitmap,
              tagTargets,
              excluded,
              true);
      if (heads != null) {
        ret.add(heads);
        excluded.add(0, heads.getIndex());
      }
    }

    deleteTempPacksIdx();

    return ret;
  }

  private static boolean isHead(Ref ref) {
    return ref.getName().startsWith(Constants.R_HEADS);
  }

  private static boolean isTag(Ref ref) {
    return ref.getName().startsWith(Constants.R_TAGS);
  }

  private void deleteTempPacksIdx() {
    Path packDir = repo.getObjectDatabase().getPackDirectory().toPath();
    Instant threshold = Instant.now().minus(1, ChronoUnit.DAYS);
    if (!Files.exists(packDir)) {
      return;
    }
    try (DirectoryStream<Path> stream =
        Files.newDirectoryStream(packDir, "gc_*_tmp")) { // $NON-NLS-1$
      stream.forEach(
          t -> {
            try {
              Instant lastModified = Files.getLastModifiedTime(t).toInstant();
              if (lastModified.isBefore(threshold)) {
                Files.deleteIfExists(t);
              }
            } catch (IOException e) {
              LOG.error(e.getMessage(), e);
            }
          });
    } catch (IOException e) {
      LOG.error(e.getMessage(), e);
    }
  }

  /**
   * @param ref the ref which log should be inspected
   * @param minTime only reflog entries not older then this time are processed
   * @return the {@link ObjectId}s contained in the reflog
   * @throws IOException
   */
  private Set<ObjectId> listRefLogObjects(Ref ref, long minTime) throws IOException {
    ReflogReader reflogReader = repo.getReflogReader(ref);
    List<ReflogEntry> rlEntries = reflogReader.getReverseEntries();
    if (rlEntries == null || rlEntries.isEmpty()) return Collections.emptySet();
    Set<ObjectId> ret = new HashSet<>();
    for (ReflogEntry e : rlEntries) {
      if (e.getWho().getWhen().getTime() < minTime) break;
      ObjectId newId = e.getNewId();
      if (newId != null && !ObjectId.zeroId().equals(newId)) ret.add(newId);
      ObjectId oldId = e.getOldId();
      if (oldId != null && !ObjectId.zeroId().equals(oldId)) ret.add(oldId);
    }
    return ret;
  }

  /**
   * Returns a collection of all refs and additional refs.
   *
   * <p>Additional refs which don't start with "refs/" are not returned because they should not save
   * objects from being garbage collected. Examples for such references are ORIG_HEAD, MERGE_HEAD,
   * FETCH_HEAD and CHERRY_PICK_HEAD.
   *
   * @return a collection of refs pointing to live objects.
   * @throws IOException
   */
  private Collection<Ref> getAllRefs() throws IOException {
    RefDatabase refdb = repo.getRefDatabase();
    Collection<Ref> refs = refdb.getRefs();
    List<Ref> addl = refdb.getAdditionalRefs();
    if (!addl.isEmpty()) {
      List<Ref> all = new ArrayList<>(refs.size() + addl.size());
      all.addAll(refs);
      // add additional refs which start with refs/
      for (Ref r : addl) {
        checkCancelled();
        if (r.getName().startsWith(Constants.R_REFS)) {
          all.add(r);
        }
      }
      return all;
    }
    return refs;
  }

  /**
   * Return a list of those objects in the index which differ from whats in HEAD
   *
   * @return a set of ObjectIds of changed objects in the index
   * @throws IOException
   * @throws CorruptObjectException
   * @throws NoWorkTreeException
   */
  private Set<ObjectId> listNonHEADIndexObjects() throws CorruptObjectException, IOException {
    if (repo.isBare()) {
      return Collections.emptySet();
    }
    try (TreeWalk treeWalk = new TreeWalk(repo)) {
      treeWalk.addTree(new DirCacheIterator(repo.readDirCache()));
      ObjectId headID = repo.resolve(Constants.HEAD);
      if (headID != null) {
        try (RevWalk revWalk = new RevWalk(repo)) {
          treeWalk.addTree(revWalk.parseTree(headID));
        }
      }

      treeWalk.setFilter(TreeFilter.ANY_DIFF);
      treeWalk.setRecursive(true);
      Set<ObjectId> ret = new HashSet<>();

      while (treeWalk.next()) {
        checkCancelled();
        ObjectId objectId = treeWalk.getObjectId(0);
        switch (treeWalk.getRawMode(0) & FileMode.TYPE_MASK) {
          case FileMode.TYPE_MISSING:
          case FileMode.TYPE_GITLINK:
            continue;
          case FileMode.TYPE_TREE:
          case FileMode.TYPE_FILE:
          case FileMode.TYPE_SYMLINK:
            ret.add(objectId);
            continue;
          default:
            throw new IOException(
                MessageFormat.format(
                    JGitText.get().corruptObjectInvalidMode3,
                    String.format(
                        "%o", //$NON-NLS-1$
                        Integer.valueOf(treeWalk.getRawMode(0))),
                    (objectId == null) ? "null" : objectId.name(), // $NON-NLS-1$
                    treeWalk.getPathString(), //
                    repo.getIndexFile()));
        }
      }
      return ret;
    }
  }

  private Pack writePack(
      @NonNull Set<? extends ObjectId> want,
      @NonNull Set<? extends ObjectId> have,
      @NonNull Set<ObjectId> tags,
      @NonNull Set<ObjectId> excludedRefsTips,
      Set<ObjectId> tagTargets,
      List<ObjectIdSet> excludeObjects,
      boolean createBitmap)
      throws IOException {
    checkCancelled();
    File tmpPack = null;
    Map<PackExt, File> tmpExts =
        new TreeMap<>(
            (o1, o2) -> {
              // INDEX entries must be returned last, so the pack
              // scanner does pick up the new pack until all the
              // PackExt entries have been written.
              if (o1 == o2) {
                return 0;
              }
              if (o1 == PackExt.INDEX) {
                return 1;
              }
              if (o2 == PackExt.INDEX) {
                return -1;
              }
              return Integer.signum(o1.hashCode() - o2.hashCode());
            });
    try (PackWriter pw = new PackWriter(pconfig, repo.newObjectReader())) {
      // prepare the PackWriter
      pw.setDeltaBaseAsOffset(true);
      pw.setReuseDeltaCommits(false);
      if (tagTargets != null) {
        pw.setTagTargets(tagTargets);
      }
      if (excludeObjects != null) for (ObjectIdSet idx : excludeObjects) pw.excludeObjects(idx);
      pw.setCreateBitmaps(createBitmap);
      pw.preparePack(pm, want, have, PackWriter.NONE, union(tags, excludedRefsTips));
      if (pw.getObjectCount() == 0) return null;
      checkCancelled();

      // create temporary files
      ObjectId id = pw.computeName();
      File packdir = repo.getObjectDatabase().getPackDirectory();
      packdir.mkdirs();
      tmpPack =
          File.createTempFile(
              "gc_", //$NON-NLS-1$
              PACK.getTmpExtension(),
              packdir);
      String tmpBase = tmpPack.getName().substring(0, tmpPack.getName().lastIndexOf('.'));
      File tmpIdx = new File(packdir, tmpBase + INDEX.getTmpExtension());
      tmpExts.put(INDEX, tmpIdx);

      if (!tmpIdx.createNewFile())
        throw new IOException(
            MessageFormat.format(JGitText.get().cannotCreateIndexfile, tmpIdx.getPath()));

      // write the packfile
      try (FileOutputStream fos = new FileOutputStream(tmpPack);
          FileChannel channel = fos.getChannel();
          OutputStream channelStream = Channels.newOutputStream(channel)) {
        pw.writePack(pm, pm, channelStream);
        channel.force(true);
      }

      // write the packindex
      try (FileOutputStream fos = new FileOutputStream(tmpIdx);
          FileChannel idxChannel = fos.getChannel();
          OutputStream idxStream = Channels.newOutputStream(idxChannel)) {
        pw.writeIndex(idxStream);
        idxChannel.force(true);
      }

      if (pw.prepareBitmapIndex(pm)) {
        File tmpBitmapIdx = new File(packdir, tmpBase + BITMAP_INDEX.getTmpExtension());
        tmpExts.put(BITMAP_INDEX, tmpBitmapIdx);

        if (!tmpBitmapIdx.createNewFile())
          throw new IOException(
              MessageFormat.format(JGitText.get().cannotCreateIndexfile, tmpBitmapIdx.getPath()));

        try (FileOutputStream fos = new FileOutputStream(tmpBitmapIdx);
            FileChannel idxChannel = fos.getChannel();
            OutputStream idxStream = Channels.newOutputStream(idxChannel)) {
          pw.writeBitmapIndex(idxStream);
          idxChannel.force(true);
        }
      }

      // rename the temporary files to real files
      File packDir = repo.getObjectDatabase().getPackDirectory();
      PackFile realPack = new PackFile(packDir, id, PackExt.PACK);

      if (realPack.exists()) {
        Iterator var3 = repo.getObjectDatabase().getPacks().iterator();

        while (var3.hasNext()) {
          Pack p = (Pack) var3.next();
          if (realPack.getPath().equals(p.getPackFile().getPath())) {
            p.close();
            break;
          }
        }
      }

      tmpPack.setReadOnly();

      FileUtils.rename(tmpPack, realPack, StandardCopyOption.ATOMIC_MOVE);
      for (Map.Entry<PackExt, File> tmpEntry : tmpExts.entrySet()) {
        File tmpExt = tmpEntry.getValue();
        tmpExt.setReadOnly();

        PackFile realExt = new PackFile(packDir, id, tmpEntry.getKey());
        try {
          FileUtils.rename(tmpExt, realExt, StandardCopyOption.ATOMIC_MOVE);
        } catch (IOException e) {
          File newExt =
              new File(realExt.getParentFile(), realExt.getName() + ".new"); // $NON-NLS-1$
          try {
            FileUtils.rename(tmpExt, newExt, StandardCopyOption.ATOMIC_MOVE);
          } catch (IOException e2) {
            newExt = tmpExt;
            e = e2;
          }
          throw new IOException(
              MessageFormat.format(JGitText.get().panicCantRenameIndexFile, newExt, realExt), e);
        }
      }
      boolean interrupted = false;
      try {
        FileSnapshot snapshot = FileSnapshot.save(realPack);
        if (pconfig.doWaitPreventRacyPack(snapshot.size())) {
          snapshot.waitUntilNotRacy();
        }
      } catch (InterruptedException e) {
        interrupted = true;
      }
      try {
        return repo.getObjectDatabase().openPack(realPack);
      } finally {
        if (interrupted) {
          // Re-set interrupted flag
          Thread.currentThread().interrupt();
        }
      }
    } finally {
      if (tmpPack != null && tmpPack.exists()) tmpPack.delete();
      for (File tmpExt : tmpExts.values()) {
        if (tmpExt.exists()) tmpExt.delete();
      }
    }
  }

  private Set<? extends ObjectId> union(Set<ObjectId> tags, Set<ObjectId> excludedRefsHeadsTips) {
    HashSet<ObjectId> unionSet = new HashSet<>(tags.size() + excludedRefsHeadsTips.size());
    unionSet.addAll(tags);
    unionSet.addAll(excludedRefsHeadsTips);
    return unionSet;
  }

  private void checkCancelled() throws CancelledException {
    if (pm.isCancelled() || Thread.currentThread().isInterrupted()) {
      throw new CancelledException(JGitText.get().operationCanceled);
    }
  }

  @SuppressWarnings("boxing")
  private boolean shouldPackKeptObjects() {
    return pconfig.isPackKeptObjects();
  }
}
