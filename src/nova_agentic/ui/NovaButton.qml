// NovaButton.qml -- PySide-Nova 基础按钮组件（纯 QML 声明式 UI）
import QtQuick 2.15

Item {
    id: root

    // ---------------------------------------------------------------- 公开属性
    property string text: "Button"
    property string iconSource: ""

    property color baseColor: "#3B82F6"
    property color hoverColor: "#2563EB"
    property color pressedColor: "#1D4ED8"
    property color textColor: "#FFFFFF"

    property int radius: 6
    property int horizontalPadding: 16
    property int verticalPadding: 8
    property int fontSize: 14

    property int animationDuration: 160

    // 供外部（Python）连接
    signal clicked()
    signal doubleClicked()
    signal hovered()
    signal unhovered()

    // ---------------------------------------------------------------- 尺寸
    implicitWidth: contentRow.implicitWidth + horizontalPadding * 2
    implicitHeight: contentRow.implicitHeight + verticalPadding * 2

    // ---------------------------------------------------------------- 背景
    Rectangle {
        id: background
        anchors.fill: parent
        radius: root.radius
        color: root.baseColor
        opacity: root.enabled ? 1.0 : 0.45

        // hover / pressed 变色动画
        Behavior on color {
            ColorAnimation {
                duration: root.animationDuration
                easing.type: Easing.OutCubic
            }
        }
    }

    // ---------------------------------------------------------------- 内容
    Row {
        id: contentRow
        anchors.centerIn: parent
        spacing: root.iconSource === "" ? 0 : 6

        Image {
            id: icon
            visible: root.iconSource !== ""
            source: root.iconSource
            width: root.fontSize
            height: root.fontSize
            fillMode: Image.PreserveAspectFit
            anchors.verticalCenter: parent.verticalCenter
        }

        Text {
            id: label
            text: root.text
            color: root.textColor
            font.pixelSize: root.fontSize
            anchors.verticalCenter: parent.verticalCenter

            Behavior on color {
                ColorAnimation {
                    duration: root.animationDuration
                    easing.type: Easing.OutCubic
                }
            }
        }
    }

    // ---------------------------------------------------------------- 交互
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: root.enabled ? Qt.PointingHandCursor : Qt.ArrowCursor

        onEntered: {
            if (!root.enabled) return
            background.color = root.hoverColor
            root.hovered()
        }

        onExited: {
            if (!root.enabled) return
            background.color = root.baseColor
            root.unhovered()
        }

        onPressed: {
            if (!root.enabled) return
            background.color = root.pressedColor
        }

        onReleased: {
            if (!root.enabled) return
            background.color = mouseArea.containsMouse ? root.hoverColor : root.baseColor
        }

        onClicked: {
            if (!root.enabled) return
            root.clicked()
        }

        onDoubleClicked: {
            if (!root.enabled) return
            root.doubleClicked()
        }
    }
}
