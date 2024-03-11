package gerritforge

import gerritforge.EncodeUtils.encode
import pureconfig._
import pureconfig.generic.auto._

import scala.concurrent.duration.FiniteDuration

object GerritTestConfig {
  val testConfig = ConfigSource.default.at("gerrit").loadOrThrow[GerritTestConfig]
}

case class GerritTestConfig(
    accountCookie: Option[String],
    xsrfToken: Option[String],
    httpUrl: Option[String],
    sshUrl: Option[String],
    project: String,
    userAgent: String,
    numUsers: Int,
    duration: FiniteDuration,
    restRunAnonymousUser: Boolean,
    reviewerAccount: Int
) {
  val encodedProject = encode(project)
}
