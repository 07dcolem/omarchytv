pragma Singleton
import QtQuick
import Quickshell
import Quickshell.Io

// One `omarchy-link session` per shell process, shared by every bar instance
// (one per monitor). It speaks JSON lines: state snapshots out, ops in.
Singleton {
  id: root

  property var state: ({ paired: false, connected: false, tv: null, foreground: null,
                         screensaver: false, homeVisible: false, capabilities: [], apps: [],
                         devices: [], discovering: false, pairing: false, error: "", lastSync: null })
  property string lastLog: ""
  property bool running: proc.running

  readonly property string cliPath: decodeURIComponent(
    String(Qt.resolvedUrl("../bin/omarchy-link")).replace(/^file:\/\//, ""))

  function send(op) {
    if (!proc.running) return false
    proc.write(JSON.stringify(op) + "\n")
    return true
  }
  function key(name) { return send({ op: "key", key: name }) }
  function launch(pkg) { return send({ op: "launch", package: pkg }) }
  function discover() { return send({ op: "discover" }) }
  function pair(address, port, code) {
    return send({ op: "pair", address: String(address), port: Number(port || 47800), code: String(code) })
  }
  function unpair() { return send({ op: "unpair" }) }
  function syncTheme() { return send({ op: "sync" }) }
  function refresh() { return send({ op: "refresh" }) }
  function castClipboard() { return send({ op: "cast" }) }
  function castStop() { return send({ op: "cast_stop" }) }

  function can(cap) {
    var caps = state.capabilities || []
    return caps.indexOf(cap) >= 0
  }

  Process {
    id: proc
    command: [root.cliPath, "session"]
    stdinEnabled: true
    running: true

    stdout: SplitParser {
      onRead: function(line) {
        var msg
        try { msg = JSON.parse(String(line || "")) } catch (e) { return }
        if (msg.event === "state" && msg.state) root.state = msg.state
        else if (msg.event === "log") root.lastLog = String(msg.message || "")
      }
    }
    stderr: SplitParser {
      onRead: function(line) { root.lastLog = String(line || "").trim() }
    }
    onExited: function() {
      var s = root.state
      s.connected = false
      root.state = s
      restart.restart()
    }
  }

  Timer {
    id: restart
    interval: 3000
    onTriggered: if (!proc.running) proc.running = true
  }
}
