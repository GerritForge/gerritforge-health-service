package com.gerritforge.ghs.actions;

import static org.eclipse.jgit.internal.storage.pack.PackExt.BITMAP_INDEX;
import static org.eclipse.jgit.internal.storage.pack.PackExt.PACK;

import com.google.common.flogger.FluentLogger;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.channels.Channels;
import java.nio.channels.FileChannel;
import java.text.MessageFormat;
import org.eclipse.jgit.internal.JGitText;
import org.eclipse.jgit.internal.storage.file.FileRepository;
import org.eclipse.jgit.internal.storage.pack.PackWriter;
import org.eclipse.jgit.lib.NullProgressMonitor;
import org.eclipse.jgit.storage.file.FileRepositoryBuilder;
import org.eclipse.jgit.storage.pack.PackConfig;

public class BitmapGenerationAction implements Action {
  private static final FluentLogger logger = FluentLogger.forEnclosingClass();

  public void prepareBitmap(FileRepository repository) throws IOException {
    File packdir = repository.getObjectDatabase().getPackDirectory();
    packdir.mkdirs();
    File tmpPack =
        File.createTempFile(
            "gc_", //$NON-NLS-1$
            PACK.getTmpExtension(),
            packdir);
    String tmpBase = tmpPack.getName().substring(0, tmpPack.getName().lastIndexOf('.'));

    try (PackWriter pw = new PackWriter(new PackConfig(repository), repository.newObjectReader())) {
      if (pw.prepareBitmapIndex(NullProgressMonitor.INSTANCE)) {
        File tmpBitmapIdx = new File(packdir, tmpBase + BITMAP_INDEX.getTmpExtension());

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
    }
  }

  @Override
  public ActionResult apply(String repositoryPath) {
    FileRepositoryBuilder repositoryBuilder =
        new FileRepositoryBuilder()
            .setGitDir(new File(repositoryPath))
            .readEnvironment()
            .findGitDir();

    try (FileRepository repository = (FileRepository) repositoryBuilder.build()) {
      prepareBitmap(repository);
    } catch (IOException e) {
      logger.atSevere().withCause(e).log(
          "Bitmap generation failed for the repository path %s", repositoryPath);
      return new ActionResult(
          false, String.format("Bitmap generation action failed, message: %s", e.getCause()));
    }

    return new ActionResult(true, "Bitmap generation action successful");
  }
}
