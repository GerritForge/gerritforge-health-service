package com.gerritforge.ghs.actions;

import java.util.Optional;

public class ActionResult {
    private boolean successful;
    private Optional<String> message;

    public ActionResult(boolean isSuccessful) {
        this.successful = isSuccessful;
    }

    public boolean isSuccessful() {
        return successful;
    }

    public Optional<String> getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = Optional.of(message);
    }

    @Override
    public String toString() {
        return "ActionResult{" +
                "successful=" + successful +
                ", message=" + message.orElse("") +
                '}';
    }
}
