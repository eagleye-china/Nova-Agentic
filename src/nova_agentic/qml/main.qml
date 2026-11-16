// src/nova_agentic/qml/main.qml
import QtQuick
import QtQuick.Controls.Basic
import QtQuick.Layouts
import Nova 1.0

ApplicationWindow {
    id: appWindow
    visible: true
    width: 1000
    height: 800
    title: "Nova-Agentic (极客直连版)"
    color: Theme.background

    NovaChat {
        id: chatWindow
        anchors.fill: parent
        title: "Nova-Orbit 🤖"
        userName: "单保录"
        userAvatar: "👨‍💻"
        aiName: "小诺 (Agentic)"
        aiAvatar: "🤖"

        Component.onCompleted: {
            ThemeManager.mode = "dark"
            Theme.mode = "dark"
            ChatBridge.setTheme("dark")
            addAiMessage("<p>你好！底层已就绪，支持 Markdown 双模渲染和一键执行啦！🚀</p>", false)
        }

        onThemeToggleRequested: {
            ThemeManager.mode = (Theme.mode === "light" ? "dark" : "light")
            ChatBridge.setTheme(ThemeManager.mode)
        }

        onMessageSent: (text) => {
            isAiThinking = true
            let timeStr = Qt.formatTime(new Date(), "hh:mm");
            model.append({
                sent: false, name: aiName, avatar: aiAvatar,
                text: "", stamp: timeStr, isTyping: false, isSystem: false
            });
            scrollToBottom();
            ChatBridge.sendMessage(text);
        }

        onCopyCodeRequested: (base64Code) => {
            ChatBridge.copyToClipboard(base64Code)
        }
    }

    Connections {
        target: ThemeManager

        function onModeChanged() {
            Theme.mode = ThemeManager.mode
        }
    }

    Connections {
        target: ChatBridge

        function onHtmlUpdated(htmlContent) {
            for (let i = chatWindow.model.count - 1; i >= 0; i--) {
                let item = chatWindow.model.get(i);
                if (!item.sent && !item.isSystem) {
                    chatWindow.model.setProperty(i, "text", htmlContent);
                    chatWindow.scrollToBottom();
                    break;
                }
            }
        }

        function onActionLogged(log) {
            chatWindow.addSystemMessage(log);
        }

        function onReplyFinished() {
            chatWindow.isAiThinking = false;
        }

        function onReplyError(err) {
            chatWindow.isAiThinking = false;
            chatWindow.addAiMessage("❌ " + err, false);
        }

        // 🌟 接收代码执行结果，作为系统消息展示
        function onCommandExecuted(result) {
            chatWindow.addSystemMessage("💻 执行结果:\n" + result);
            chatWindow.isAiThinking = false;
        }
    }
}