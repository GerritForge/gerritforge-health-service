package com.gerritforge.ghs.actions;

import java.util.Optional;

public class ActionResult {
  private final boolean successful;
  private final Optional<String> message;

  public ActionResult(boolean isSuccessful) {
    this(isSuccessful, null);
  }

  public ActionResult(boolean isSuccessful, String message) {
    this.successful = isSuccessful;
    this.message = Optional.ofNullable(message);
  }

  public boolean isSuccessful() {
    return successful;
  }

  public Optional<String> getMessage() {
    return message;
  }

  @Override
  public String toString() {
    return "ActionResult{" + "successful=" + successful + ", message=" + message.orElse("") + '}';
  }
}
