// Copyright (C) 2024 GerritForge, Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package com.gerritforge.ghs.actions;

import static com.gerritforge.ghs.actions.FileRepositoryFactory.create;

import com.google.common.flogger.FluentLogger;
import java.io.File;
import java.io.IOException;
import java.util.Collection;
import java.util.List;
import java.util.stream.Collectors;
import org.eclipse.jgit.internal.storage.file.FileReftableDatabase;
import org.eclipse.jgit.internal.storage.file.FileRepository;
import org.eclipse.jgit.internal.storage.file.RefDirectory;
import org.eclipse.jgit.lib.Constants;
import org.eclipse.jgit.lib.Ref;
import org.eclipse.jgit.lib.RefDatabase;

public class PackRefsAction implements Action {
  private static final FluentLogger logger = FluentLogger.forEnclosingClass();

  @Override
  public ActionResult apply(String repositoryPath) {
    try (FileRepository repo = create(new File(repositoryPath))) {
      RefDatabase refDb = repo.getRefDatabase();

      if (refDb instanceof FileReftableDatabase) {
        return new ActionResult(
            false,
            String.format(
                "Ref-table of repository %s is not supported yet for repacking", repositoryPath));
      }

      Collection<Ref> refs = refDb.getRefsByPrefix(Constants.R_REFS);
      List<String> refsToBePacked =
          refs.stream()
              .filter(r -> !r.isSymbolic())
              .filter(r -> r.getStorage().isLoose())
              .map(Ref::getName)
              .collect(Collectors.toList());
      ((RefDirectory) repo.getRefDatabase()).pack(refsToBePacked);
      return new ActionResult(true);
    } catch (IOException e) {
      logger.atSevere().withCause(e).log(
          "Packed refs generation failed for the repository path %s", repositoryPath);
      return new ActionResult(
          false, String.format("Packed refs generation action failed, message: %s", e.getCause()));
    }
  }
}
