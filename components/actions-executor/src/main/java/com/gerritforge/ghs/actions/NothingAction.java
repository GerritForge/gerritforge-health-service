package com.gerritforge.ghs.actions;

import java.util.concurrent.Callable;

public class NothingAction implements Callable<ActionResult> {
    @Override
    public ActionResult call() throws Exception {
        ActionResult result = new ActionResult(true);
        result.setMessage("NoOp action executed successfully");
        return result;
    }
}
