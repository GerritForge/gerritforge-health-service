import Dependencies._

ThisBuild / scalaVersion := "2.13.12"
ThisBuild / version := "0.1.0-SNAPSHOT"
ThisBuild / organization := "com.gerritforge"
ThisBuild / organizationName := "GerritForge"

// For scalafix
ThisBuild / semanticdbEnabled := true
ThisBuild / semanticdbVersion := scalafixSemanticdb.revision

val pluginName = "ghs-collector"
val pluginDescription = "GHS collector for Gerrit"

lazy val root = (project in file("."))
  .settings(
    name := "ghs.collectors.gerrit",
    libraryDependencies ++= Seq(
      kamon,
      logback,
      gerritPluginApi,
      scalaLogging,
      scalaTest % Test,
      sttp % Test
    ),
    assembly / assemblyJarName := s"$pluginName.jar",
    assembly / assemblyMergeStrategy := {
      case "module-info.class"                                => MergeStrategy.discard
      case x =>
        val oldStrategy = (ThisBuild / assemblyMergeStrategy).value
        oldStrategy(x)
    },
    Compile / packageBin / packageOptions += Package.ManifestAttributes(
      ("Gerrit-ApiType", "plugin"),
      ("Gerrit-PluginName", pluginName),
      ("Gerrit-Module", "com.gerritforge.ghs.collectors.gerrit.CollectorModule"),
      ("Gerrit-HttpModule", "com.gerritforge.ghs.collectors.gerrit.HttpModule"),
      ("Implementation-Title", pluginDescription),
      ("Implementation-URL", "https://github.com/GerritForge/gerritforge-health-service")
    )
  )