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

import java.nio.file.Files;
import java.nio.file.Path;
import org.eclipse.jgit.api.Git;
import org.eclipse.jgit.api.errors.GitAPIException;
import org.eclipse.jgit.lib.Ref;
import org.eclipse.jgit.revwalk.RevCommit;
import org.eclipse.jgit.transport.RefSpec;
import org.junit.After;
import org.junit.Before;
import org.junit.Rule;
import org.junit.rules.TestName;

abstract class GitActionTest {
  protected static final Path TEST_TMP_PREFIX = Path.of("/tmp");
  protected static final String TEST_AUTHOR = "Test Author";
  protected static final String TEST_AUTHOR_EMAIL = "test@author.com";
  protected static final String TEST_COMMIT_MESSAGE = "Test commit message";
  protected static final String TEST_BRANCH = "test-branch";
  public static final String ALL_REFS_SPEC = "refs/*:refs/*";

  @Rule public TestName name = new TestName();
  protected Path testRepoPath;
  protected Git testRepoGit;
  protected Path testCloneRepoPath;
  protected String gitRepoUri;

  @Before
  public void setup() throws Exception {
    testRepoPath = Files.createTempDirectory(TEST_TMP_PREFIX, sanitisedTestName());
    gitRepoUri = "file://" + testRepoPath;

    testCloneRepoPath = Files.createTempDirectory(TEST_TMP_PREFIX, sanitisedTestName());
    testRepoGit = Git.init().setBare(true).setDirectory(testRepoPath.toFile()).call();
  }

  @After
  public void teardown() throws Exception {
    testRepoGit.close();
  }

  protected String sanitisedTestName() {
    return this.getClass().getSimpleName() + "_" + name.getMethodName();
  }

  protected Ref pushNewCommitToBranch() throws GitAPIException {
    Git git =
        Git.cloneRepository().setURI(gitRepoUri).setDirectory(testCloneRepoPath.toFile()).call();
    RevCommit commit =
        git.commit()
            .setAuthor(TEST_AUTHOR, TEST_AUTHOR_EMAIL)
            .setMessage(TEST_COMMIT_MESSAGE)
            .call();
    Ref branch = git.branchCreate().setName(TEST_BRANCH).setStartPoint(commit.getName()).call();
    git.push().setForce(true).setRefSpecs(new RefSpec(ALL_REFS_SPEC)).setRemote(gitRepoUri).call();
    return branch;
  }
}
