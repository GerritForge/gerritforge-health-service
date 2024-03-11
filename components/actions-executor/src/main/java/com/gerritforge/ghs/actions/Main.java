package com.gerritforge.ghs.actions;

import com.google.common.flogger.FluentLogger;
import java.util.concurrent.Callable;

public class Main {
  private static final FluentLogger logger = FluentLogger.forEnclosingClass();

  public static void main(String[] args) {
    String action = args[0];
    String className = Main.class.getPackageName() + "." + action;

    try {
      Class<Callable<ActionResult>> actionClass =
          (Class<Callable<ActionResult>>) Class.forName(className);
      ActionResult result = actionClass.getDeclaredConstructor().newInstance().call();
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
}
