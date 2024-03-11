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

import com.google.common.flogger.FluentLogger;

import static java.lang.System.exit;

public class Main {
  private static final FluentLogger logger = FluentLogger.forEnclosingClass();

  public static void main(String[] args) {
    if (args.length < 2) {
      printUse();
      exit(-1);
    }

    String action = args[0];
    String repositoryPath = args[1];
    String className = Main.class.getPackageName() + "." + action;

    try {
      Class<Action> actionClass = (Class<Action>) Class.forName(className);
      ActionResult result =
          actionClass.getDeclaredConstructor().newInstance().apply(repositoryPath);
      logger.atInfo().log(result.toString());
    } catch (ClassNotFoundException e) {
      logger.atSevere().withCause(e).log("Cannot find action class for action name:%s", action);
    } catch (InstantiationException | IllegalAccessException e) {
      logger.atSevere().withCause(e).log("Cannot instantiate action class %s", className);
    } catch (Exception e) {
      logger.atSevere().withCause(e).log(
          "Exception during the action execution. Action class: %s", className);
    }
  }

  private static void printUse() {
    logger.atInfo().log("Use: java %s <actionName> <repositoryPath>", Main.class.getName());
    System.err.printf("Use: java %s <actionName> <repositoryPath>%n", Main.class.getName());
  }
}
