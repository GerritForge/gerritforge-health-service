package gerritforge

import com.github.barbasa.gatling.git.GitRequestSession.MasterRef
import com.github.barbasa.gatling.git.protocol.GitProtocol
import com.github.barbasa.gatling.git.request.builder.GitRequestBuilder
import com.github.barbasa.gatling.git.{GatlingGitConfiguration, GitRequestSession}
import gerritforge.GerritTestConfig.testConfig
import io.gatling.core.Predef._
import io.gatling.core.structure.ScenarioBuilder

import java.util.concurrent.TimeUnit
import scala.concurrent.duration.FiniteDuration

class GerritGHSSimulation extends Simulation {
  implicit val gitConfig      = GatlingGitConfiguration()
  private val httpUrl: String = testConfig.httpUrl.get

  val refSpecFeeder =
    (1 to testConfig.numUsers) map { _ =>
      Map("refSpec" -> MasterRef)
    }

  private val pauseLength = FiniteDuration(3, TimeUnit.SECONDS)
  private val pauseStdDev = normalPausesWithStdDevDuration(FiniteDuration(1, TimeUnit.SECONDS))

  private val httpClonePct = 0.82
  private val httpCloneDuration =
    FiniteDuration((testConfig.duration * httpClonePct).toSeconds, TimeUnit.SECONDS)
  private val httpClone: ScenarioBuilder = scenario(s"Clone Command over HTTP")
    .feed(refSpecFeeder.circular)
    .pause(
      pauseLength,
      pauseStdDev
    )
    .exec(
      new GitRequestBuilder(
        GitRequestSession(
          "clone",
          s"$httpUrl/${testConfig.project}",
          s"#{refSpec}",
          ignoreFailureRegexps = List(".*want.+not valid.*")
        )
      )
    )

  setUp(
    httpClone
      .inject(
        constantConcurrentUsers(testConfig.numUsers) during httpCloneDuration
      )
      .protocols(GitProtocol)
  ).maxDuration(testConfig.duration)
}
