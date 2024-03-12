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

import static com.google.common.truth.Truth.assertThat;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Optional;
import org.eclipse.jgit.lib.Ref;
import org.junit.Test;

public class BitmapGenerationActionTest extends GitActionTest {

  @Test
  public void applyBitmapGenerationActionShouldGenerateBitMap() throws Exception {
    Ref branch = pushNewCommitToBranch();
    Optional<Path> packFile =
        Files.list(testRepoPath.resolve("objects/pack"))
            .filter(p -> p.toString().endsWith(".pack"))
            .findFirst();
    assertThat(packFile).isPresent();
    String bitmapFileName = packFile.get().toString().replace(".pack", ".bitmap");
    File bitmapFile = new File(bitmapFileName);
    assertThat(bitmapFile.exists()).isFalse();

    assertThat(new BitmapGenerationAction().apply(testRepoPath.toString()).isSuccessful()).isTrue();
    assertThat(bitmapFile.exists()).isTrue();
  }
}
