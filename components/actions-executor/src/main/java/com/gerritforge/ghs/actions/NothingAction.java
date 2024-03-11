package com.gerritforge.ghs.actions;

import java.util.concurrent.Callable;

public class NothingAction implements Callable<ActionResult> {
  @Override
  public ActionResult call() throws Exception {
    return new ActionResult(true, "NoOp action executed successfully");
  }
}
