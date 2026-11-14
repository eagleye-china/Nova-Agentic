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
    title: "Nova-Agentic (终极 QML 版)"
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
            if (typeof ThemeManager !== "undefined" && ThemeManager !== null) {
                Theme.mode = ThemeManager.mode;
            }
            addAiMessage("你好！我是你的 AI 架构师小诺。请先点击右上角【配置 API Key】，然后我们就可以开始对话了！🚀", false)
        }

        onMessageSent: (text) => {
            isAiThinking = true
            let timeStr = Qt.formatTime(new Date(), "hh:mm");
            model.append({sent: false, name: aiName, avatar: aiAvatar, text: "", stamp: timeStr, isTyping: false});
            scrollToBottom()
            ChatBridge.sendMessage(text)
        }
    }

    Connections {
        target: ChatBridge

        function onChunkReceived(chunk) {
            let lastIndex = chatWindow.model.count - 1;
            if (lastIndex >= 0) {
                let currentText = chatWindow.model.get(lastIndex).text;
                chatWindow.model.setProperty(lastIndex, "text", currentText + chunk);
                chatWindow.scrollToBottom();
            }
        }

        function onActionLogged(log) {
            if (log.startsWith("RENDER_HTML:")) {
                let final_text = log.replace("RENDER_HTML:", "");
                let lastIndex = chatWindow.model.count - 1;
                if (lastIndex >= 0) {
                    chatWindow.model.setProperty(lastIndex, "text", final_text);
                }
                return;
            }
            chatWindow.addSystemMessage(log);
        }

        function onReplyFinished() {
            chatWindow.isAiThinking = false;
        }

        function onReplyError(err) {
            chatWindow.isAiThinking = false;
            chatWindow.addAiMessage("❌ **API 请求失败**: " + err, false);
            if (err.indexOf("API Key") > -1) {
                apiKeyDialog.visible = true
            }
        }
    }

    // 浮动配置按钮
    Rectangle {
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: Units.px(20)
        width: Units.px(100)
        height: Units.px(36)
        radius: Theme.radiusSm
        color: Theme.primary
        z: 1000

        Text {
            anchors.centerIn: parent
            text: "配置 API Key"
            color: Theme.white
            font.pixelSize: Units.px(12)
        }

        MouseArea {
            anchors.fill: parent
            cursorShape: Qt.PointingHandCursor
            onClicked: apiKeyDialog.visible = true
        }
    }

    // 纯安全的 API Key 弹窗
    Rectangle {
        id: apiKeyDialog
        visible: false
        anchors.centerIn: parent
        width: Units.px(400)
        height: Units.px(180)
        color: Theme.surface
        radius: Theme.radiusMd
        border.color: Theme.border
        border.width: 1
        z: 999

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: Units.px(16)
            spacing: Units.px(16)

            Text {
                text: "请配置 DeepSeek API Key (sk-...):"; color: Theme.text_primary; font.bold: true
            }

            TextField {
                id: apiKeyInput
                Layout.fillWidth: true
                placeholderText: "sk-..."
                color: Theme.text_primary
                background: Rectangle {
                    color: Theme.background; border.color: Theme.border; radius: Theme.radiusSm
                }
            }

            RowLayout {
                Layout.fillWidth: true
                Item {
                    Layout.fillWidth: true
                }
                Button {
                    text: "取消"
                    onClicked: apiKeyDialog.visible = false
                }
                Button {
                    text: "保存"
                    onClicked: {
                        if (apiKeyInput.text.trim().length > 0) {
                            ChatBridge.saveApiKey(apiKeyInput.text.trim());
                            apiKeyDialog.visible = false;
                        }
                    }
                }
            }
        }
    }
}