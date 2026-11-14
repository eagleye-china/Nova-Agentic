// src/pyside_nova/qml/NovaChatMessage.qml
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    width: parent ? parent.width : 600
    height: layoutRow.implicitHeight + 10

    // ================== 属性定义 ==================
    property string text: ""
    property bool sent: false // 发送方(右) vs 接收方(左)
    property string avatarText: ""
    property string name: ""
    property string stamp: ""
    property color bubbleColor: sent ? "#0277BD" : "#263238"
    property color textColor: "#ECEFF1"

    RowLayout {
        id: layoutRow
        width: parent.width
        spacing: 12
        layoutDirection: root.sent ? Qt.RightToLeft : Qt.LeftToRight

        // 1. 头像
        Rectangle {
            Layout.alignment: Qt.AlignTop
            width: 36
            height: 36
            radius: 18
            color: root.sent ? "#0288D1" : "#455A64"
            visible: root.avatarText !== ""

            Text {
                anchors.centerIn: parent
                text: root.avatarText
                color: "white"
                font.bold: true
                font.pixelSize: 14
            }
        }

        // 2. 气泡与元信息容器
        Column {
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignTop
            spacing: 4

            // 名字和时间 (可选)
            Text {
                text: root.name + (root.name && root.stamp ? "  " : "") + root.stamp
                color: "#78909C"
                font.pixelSize: 11
                visible: text !== ""
                anchors.right: root.sent ? parent.right : undefined
                anchors.left: root.sent ? undefined : parent.left
            }

            // 气泡本体
            Rectangle {
                width: Math.min(bubbleText.implicitWidth + 30, root.width * 0.7)
                height: bubbleText.implicitHeight + 24
                radius: 10
                color: root.bubbleColor

                // 对齐方式
                anchors.right: root.sent ? parent.right : undefined
                anchors.left: root.sent ? undefined : parent.left

                // 简单的气泡小尾巴（可选，这里用圆角代替，追求极简）
                Rectangle {
                    width: 10; height: 10; radius: 5
                    color: root.bubbleColor
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: -3
                    x: root.sent ? parent.width - 15 : 5
                    z: -1
                }

                Text {
                    id: bubbleText
                    text: root.text
                    textFormat: Text.RichText // 支持基础 HTML
                    color: root.textColor
                    wrapMode: Text.Wrap
                    width: parent.width - 30
                    anchors.centerIn: parent
                    font.pixelSize: 14
                    lineHeight: 1.3
                }
            }
        }

        // 占位符，为了让气泡在未撑满时也能正确靠边
        Item {
            Layout.fillWidth: true
            visible: false
        }
    }
}