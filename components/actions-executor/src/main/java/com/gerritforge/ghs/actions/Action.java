package com.gerritforge.ghs.actions;

import java.util.function.Function;

@FunctionalInterface
public interface Action extends Function<String, ActionResult> {}
