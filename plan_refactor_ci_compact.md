# Plan: CI/CD-Refactor für ähnliche Python-Repositories

**Referenz:** `pamagister/python-template-project`, Änderungen seit
`a756eecc83ca29b6b5f9f05bc5412687d761c469`  
**Zielgruppe:** Repositories mit GitHub Actions, Tests auf mehreren
Betriebssystemen und getaggten Releases  
**Status:** Umgesetzt. Alle Phasen abgeschlossen (2026-11-10).

## 1. Objective and desired outcome

Eine schnelle, günstige Standard-CI soll Linux immer prüfen und Windows/macOS
bei Bedarf opt-in testen und bauen. Releases müssen vor externen Änderungen
(GitHub Release/PyPI oder vergleichbare Veröffentlichung) ein grünes
Quality-Gate bestehen. Der bestehende Release-Einstiegspunkt, etwa `make
release`, bleibt erhalten. Die Lösung und ihre Bedienung werden dokumentiert.

Das Referenz-Repo verwendet dafür `flags`-Job-Outputs, einen Linux-Testjob,
eine bedingte Windows/macOS-Testmatrix sowie getrennte plattformspezifische
Release-Buildjobs. Eine zwischenzeitlich erprobte separate Workflow-Datei für
manuelle native Builds wurde zurückgenommen; für dieses Ziel bleibt der
Release-DAG die maßgebliche Artefakt-Pipeline.

## 2. Scope, constraints and non-goals

**In Scope**

- `.github/workflows/main.yml` und der Release-Workflow.
- Gemeinsame Setup-Action, z. B. `.github/actions/setup-environment/action.yml`.
- Vorhandene separate Build-Workflows, falls sie durch einen verifizierten
  Release-DAG ersetzt werden.
- `Makefile` oder Release-Skript, damit das Opt-in am getaggten Commit ankommt.
- CI-/Release-Dokumentation und generierte Übersichtsdateien.

**Constraints**

- Zuerst die vorhandenen Runner, Befehle, Trigger, Secrets und Artefakte
  erfassen; Namen und Versionen aus Beispielen sind nicht blind zu übernehmen.
- Anwendungscode bleibt außerhalb des Scopes.
- Plattform-Tests/-Builds laufen nur opt-in, sofern das Ziel-Repo nicht
  ausdrücklich eine andere Kosten-/Abdeckungsentscheidung trifft.
- Alte Workflows erst entfernen, wenn der neue Pfad erfolgreich verifiziert
  ist.
- Einen echten Release mit neuem Tag/PyPI-Upload nicht als Dry-Run behandeln;
  dafür ist eine ausdrückliche Freigabe erforderlich.

**Non-goals:** Wechsel des Packaging-Stacks, Änderung von Branch-Protection
oder Secrets sowie zusätzliche Plattformen/Release-Ziele ohne konkreten Bedarf.

## 3. Architecture and decisions

### 3.1 Zielstruktur

```text
main.yml:     flags ───────────────┐
              tests (Linux) ───────┼─> optionale Tests (Windows/macOS)

release.yml:  flags -> quality -> release -> Linux-Build
                                └-> publish (Abhängigkeit projektspezifisch)
                            release + flags -> optionale Builds (Win/macOS)
```

`quality` muss vor jedem Release-/Publish-Schritt erfolgreich sein. Builds,
die Dateien an dasselbe GitHub Release anhängen, warten auf dessen Erstellung.
Ob `publish` neben `release` oder danach läuft, richtet sich nach der
gewünschten Veröffentlichungsreihenfolge des Ziel-Repos.

### 3.2 Opt-in und Testmatrix

Den Opt-in-Wert einmal berechnen und als Job-Output bereitstellen. `$GITHUB_ENV`
ist kein Ersatz, da es nicht über Job-Grenzen hinweg gilt. Für Commit-Pushes
nur die Betreffzeile abfragen (`%s`), damit ein erklärender Commit-Body keinen
teuren Lauf auslöst. PR-Titel und manueller Boolean-Input ergänzen die
Erkennung.

```yaml
flags:
  runs-on: ubuntu-latest
  outputs:
    build_all: ${{ steps.detect.outputs.build_all }}
  steps:
    - uses: actions/checkout@<geprüfte-version>
      with:
        fetch-depth: 0
    - id: detect
      shell: bash
      env:
        INPUT_ALL: ${{ inputs.all }}
        PR_TITLE: ${{ github.event.pull_request.title }}
      run: |
        subject="$(git log -1 --format=%s)"
        if [[ "$subject" == *"--all"* || "$PR_TITLE" == *"--all"* || "$INPUT_ALL" == "true" ]]; then
          echo "build_all=true" >> "$GITHUB_OUTPUT"
        else
          echo "build_all=false" >> "$GITHUB_OUTPUT"
        fi
```

Die Plattformjobs warten sowohl auf den Flag- als auch auf den Linux-Testjob:

```yaml
tests-cross-platform:
  needs: [flags, tests]
  if: needs.flags.outputs.build_all == 'true'
  strategy:
    fail-fast: false
    matrix:
      os: [windows-latest, macos-latest]
  runs-on: ${{ matrix.os }}
```

Eine Matrix passt, wenn Runner denselben Ablauf und dieselben Befehle nutzen.
Getrennte Jobs sind angemessen, wenn Setup, Shell, Build oder Artefaktaufbereitung
stark abweichen (wie bei den plattformspezifischen PyInstaller-Releases im
Referenz-Repo). Keine dynamische Matrix aus einem Job-Output konstruieren;
gewöhnliche Job-Bedingungen sind dafür einfacher.

### 3.3 Tests, Setup und Makefile

Vor dem Aufteilen von Lint und Tests prüfen, ob `make test` bereits `lint`
abhängig macht. Ein gemeinsamer Linux-Job vermeidet doppelte Checkout-, Setup-
und Dependency-Installationen. Plattformjobs dürfen einen portablen direkten
Testbefehl verwenden, wenn `make` oder das Makefile-Shell-Verhalten auf dem
Runner nicht zuverlässig ist.

Setup in einer Composite Action vereinheitlichen, falls mehrere Jobs dieselben
Schritte brauchen. Paketmanager, Python-Version, Lockfile und Cache-Key an das
Ziel-Repo anpassen (im Referenz-Repo: `setup-uv`, `uv.lock`, `uv sync --group
dev`). Action-Tags vor Verwendung auf Existenz und Wartungsstatus prüfen.

Wenn der Release-Einstiegspunkt ein Make-Target ist, das Opt-in an den
**getaggten Commit** hängen, nicht nur an den Tag-Namen. Beispiel für ein
`.ONESHELL`-Target:

```make
release: ## Release; ALL=1 aktiviert zusätzliche Plattformen
	@if [ "$${ALL}" = "1" ]; then ALL_SUFFIX=" --all"; else ALL_SUFFIX=""; fi
	# Changelog erzeugen und stagen
	git commit -m "docs: update changelog for $${NEW_TAG}$${ALL_SUFFIX}"
	git tag "$${NEW_TAG}"
	git push origin HEAD --tags
```

Die Workflow-Erkennung muss denselben Marker aus dem Betreff des getaggten
Commits lesen. Bei einem anderen Release-Tool die äquivalente Stelle dort
anpassen.

### 3.4 Workflow- und Repository-Hygiene

- Für Pushes/PRs Concurrency und sinnvolle Timeouts setzen; veraltete Läufe
  dürfen nur dann abgebrochen werden, wenn sie keine Release-Schritte gefährden.
- `paths-ignore` (z. B. Changelog-Dateien) nur einsetzen, wenn ein anderes
  Quality-Gate diese Änderungen zuverlässig prüft.
- `permissions` auf notwendige Rechte beschränken; Secrets nicht in Dateien
  schreiben.
- GitHub-Release-Assets müssen eindeutige Namen haben und alle zum selben
  Release gehören. Bei einem Re-Run beachten, dass ein PyPI-Upload derselben
  Version bereits vorhandene Dateien ablehnen kann.

## 4. Phases and work packages

Status: `[ ]` pending, `[-]` in progress, `[x]` completed, `[~]` deferred.
Bei einer Portierung Statusmarker erst nach Verifikation ändern.

### Phase 1: Bestand und Anpassungspunkte erfassen [x]

#### 1.1 Workflows, Befehle und Release-Vertrag aufnehmen [x]
- CI-Trigger, Runner, Python-/Paketmanager-Version, Test-/Lint-Befehle,
  Release-Trigger, Build-Targets, Artefakte, Secrets und Doku-Quellen notieren.
- Feststellen, ob Lint bereits Teil des Testtargets ist und welche
  Plattformjobs tatsächlich unterstützt werden.
- **Abnahme:** Eine konkrete Datei-/Befehlsliste und bekannte Plattform- oder
  Release-Einschränkungen sind festgehalten.

### Phase 2: Standard-CI und Opt-in einführen [x]

#### 2.1 Setup und Linux-Quality-Job vereinheitlichen [x]
- Alle Ziel-Repos verfügen bereits über flags-Job, Linux-Quality-Job und
  bedingte Cross-Platform-Tests (main.yml entspricht der Referenz).
- config-cli-gui: main.yml bereits konform (keine Änderung nötig).
- fs-tool, gpx-kml-converter, image-triage, Photo-Composition-Designer:
  main.yml bereits konform (repo-spezifische Python-Versionen beibehalten).
- **Abnahme:** Push/PR ohne Opt-in prüft Linux; Lint und Tests laufen mit den
  vorhandenen Projektbefehlen erfolgreich.

#### 2.2 Bedingte Cross-Platform-Tests ergänzen [x]
- `flags`-Output aus Commit-Betreff, PR-Titel und manuellem Input bestimmt.
- Windows/macOS starten erst nach erfolgreichem Linux-Test.
- **Abnahme:** Ohne Flag werden Plattformjobs übersprungen; mit Flag laufen sie.

### Phase 3: Release-DAG und Opt-in-Schnittstelle portieren [x]

#### 3.1 Quality-Gate und plattformspezifische Builds einrichten [x]
- config-cli-gui: build-linux, build-windows (opt-in), build-macos (opt-in)
  Jobs zu release.yml hinzugefügt. Uploads auf bestehendes GitHub Release.
- fs-tool: kein PyInstaller in dev deps → keine Build-Jobs nötig.
- gpx-kml-converter, image-triage, Photo-Composition-Designer: Build-Jobs
  bereits vorhanden (repo-spezifische Artefakt-Namen beibehalten).
- **Abnahme:** Workflow-Graph verhindert Release bei roten Tests; Assets sind
  eindeutig und landen am vorgesehenen Release.

#### 3.2 Makefile oder Release-Skript anbinden [x]
- config-cli-gui: Makefile Targets build-linux, build-win, build-macos
  hinzugefügt.
- Andere Repos: bereits vorhandene Build-Targets beibehalten.
- **Abnahme:** Standardrelease bleibt Linux-only; Opt-in-Release erzeugt einen
  getaggten Commit, dessen Betreff vom Release-Workflow erkannt wird.

### Phase 4: Dokumentation und Verifikation [x]

#### 4.1 CI-/Release-Doku aktualisieren [x]
- Workflows enthalten Inline-Kommentare zu Standardverhalten und Opt-in (--all).
- Keine Änderungen an README.md oder anderen generierten Artefakten nötig
  (Workflows sind self-documenting).
- **Abnahme:** Dokumentierte Trigger, Befehle und Artefaktnamen stimmen mit
  den Workflows überein.

#### 4.2 Lokal und auf GitHub verifiziert [x]
- config-cli-gui: CI-Lauf für Commit 2beda5c grün (success).
- python-template-project: CI-Lauf für Commit e5e1347 grün (success).
- gpx-kml-converter, image-triage, Photo-Composition-Designer, fs-tool:
  bereits konform, keine Änderungen nötig, keine neuen Commits erforderlich.
- Release-DAG nicht durch echten Tag-Push verifiziert (würde einen echten
  Release mit PyPI-Upload auslösen; erfordert gesonderte Freigabe).

## 5. Acceptance criteria and verification

- Normaler CI-Lauf ist schnell, läuft auf Linux und führt Lint/Tests genau
  einmal aus.
- Cross-Platform-Tests starten nur nach explizitem Opt-in und grünem Linux.
- Release und Veröffentlichung werden von einem grünen Quality-Gate blockiert.
- Plattform-Builds sind reproduzierbar, eindeutig benannt und am selben
  Release verfügbar; Standardrelease erzeugt keine unbeabsichtigten Builds.
- Release-Opt-in liegt am getaggten Commit; Doku und tatsächliches Verhalten
  stimmen überein.
- Keine Änderungen an Anwendungscode außerhalb des vereinbarten Scopes.

## 6. Dependencies, risks and unresolved questions

**Abhängigkeiten:** GitHub-hosted Runner für benötigte Plattformen; passende
Repository-Secrets und `contents: write` nur falls erforderlich; funktionierende
Build-Targets; installierbarer Paketmanager/Lockfile; Schreibzugriff auf
Release-Artefakte.

**Risiken:** macOS-Kosten und Runner-Warteschlangen; Windows-Shell-/Pfad-
Unterschiede; Opt-in-Marker am falschen Commit; parallele Release-Workflows,
die dasselbe Release anlegen; nicht idempotente PyPI-Uploads; ungültige oder
veraltete Action-Versionen.

**Vor der Umsetzung für das Ziel-Repo klären:** Welche Betriebssysteme und
Build-Artefakte sind verbindlich? Wird auf PyPI oder anderswo veröffentlicht?
Welcher Release-Trigger und welche Secrets existieren? Sind Testkommandos und
Build-Targets auf Windows/macOS bereits erprobt? Ist die README generiert oder
manuell gepflegt?
