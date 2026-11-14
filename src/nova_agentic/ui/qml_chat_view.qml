import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Window {
    width: 900
    height: 700
    visible: true
    title: "Nova Agent (QML Version)"
    color: "#121212"

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 15
        spacing: 10

        ListView {
            id: listView
            Layout.fillWidth: true
            Layout.fillHeight: true
            model: bridge.messagesModel
            spacing: 15
            clip: true

            delegate: Item {
                width: listView.width
                height: bubbleRect.height + 10

                Rectangle {
                    id: bubbleRect
                    // 对齐逻辑：用户靠右，系统/AI 靠左
                    anchors.right: model.isUser ? parent.right : undefined
                    anchors.left: model.isUser ? undefined : parent.left

                    width: Math.min(bubbleText.implicitWidth + 30, listView.width * 0.75)
                    height: bubbleText.implicitHeight + 24
                    radius: model.isSystem ? 4 : 10 // 系统消息圆角小一点

                    // 颜色区分：用户(蓝)，系统(绿底/绿框)，AI(深灰)
                    color: model.isUser ? "#0277BD" : (model.isSystem ? "#1E272E" : "#263238")
                    border.color: model.isSystem ? "#2E7D32" : "transparent"
                    border.width: model.isSystem ? 1 : 0

                    Text {
                        id: bubbleText
                        text: model.text || ""
                        anchors.centerIn: parent
                        width: parent.width - 30
                        wrapMode: Text.Wrap
                        clip: true
                        color: model.isSystem ? "#4CAF50" : "#ECEFF1" // 系统消息文字变绿
                        font.pixelSize: model.isSystem ? 12 : 14
                        font.family: model.isSystem ? "Consolas" : "Microsoft YaHei"
                    }
                }
            }
            onCountChanged: listView.positionViewAtEnd()
        }

        // ================= 输入区 =================
        Rectangle {
            Layout.fillWidth: true
            height: 60
            radius: 8
            color: "#263238"
            border.color: "#37474F"

            TextInput {
                id: inputField
                anchors.left: parent.left
                anchors.right: customSendBtn.left
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.leftMargin: 15
                anchors.rightMargin: 15 // 给按钮留出间距
                color: "#ECEFF1"
                font.pixelSize: 14
                verticalAlignment: TextInput.AlignVCenter
                clip: true
                Keys.onReturnPressed: customSendBtn.clicked()

                Text {
                    text: "输入你的问题... (回车发送)"
                    color: "#78909C"
                    visible: inputField.text === ""
                    anchors.verticalCenter: parent.verticalCenter
                }
            }

            // ✅ 使用你刚刚 AI 生成的旗舰级按钮 NovaButton1
            NovaButton {
                id: customSendBtn
                text: "发送 🚀"
                anchors.right: parent.right
                anchors.rightMargin: 10
                anchors.verticalCenter: parent.verticalCenter

                // 设置尺寸
                width: 80
                height: 40

                // 自定义颜色（使用 QML 里定义的属性）
                baseColor: "#0277BD"
                hoverColor: "#0288D1"
                pressedColor: "#01579B"
                radius: 6

                onClicked: {
                    let msg = inputField.text.trim()
                    if (msg === "") return
                    bridge.send_user_message(msg)
                    inputField.text = ""
                }
            }
        }
    }
}