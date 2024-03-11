package com.gerritforge.ghs.actions;


public class NothingAction implements Action {
  @Override
  public ActionResult apply(String repositoryPath) {
    return new ActionResult(true, "NoOp action executed successfully");
  }
}
