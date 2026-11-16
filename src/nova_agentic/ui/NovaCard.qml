// NovaCard.qml -- PySide-Nova 基础卡片组件（圆角 + 阴影 + 标题 + 按钮）
import QtQuick
import QtQuick.Effects

Item {
    id: root

    // ---------------------------------------------------------------- 公开属性
    property string title: "卡片标题"
    property string subtitle: ""

    // 按钮部分（内部复用 NovaButton.qml，可直接替换成 QtQuick.Controls 的 Button）
    property string buttonText: "确定"
    property bool showButton: true

    // 配色
    property color cardColor: "#FFFFFF"
    property color titleColor: "#1F2937"
    property color subtitleColor: "#6B7280"
    property color borderColor: "#E5E7EB"

    // 外观
    property int radius: 12
    property int padding: 20
    property int titleFontSize: 18
    property int subtitleFontSize: 13
    property int contentSpacing: 12

    // 阴影
    property bool shadowEnabled: true
    property color shadowColor: "#33000000"
    property int shadowBlur: 24
    property int shadowYOffset: 6

    // 供外部（Python）连接
    signal buttonClicked()

    // 默认内容插槽：外部可以往里塞子元素
    default property alias contentChildren: contentColumn.data

    // ---------------------------------------------------------------- 尺寸
    implicitWidth: 320
    implicitHeight: contentColumn.implicitHeight + padding * 2

    // ---------------------------------------------------------------- 阴影层
    // 用一个单独的下层 Rectangle 做模糊，避免 MultiEffect 把卡片内容一起糊掉
    Rectangle {
        id: shadowLayer
        anchors.fill: card
        anchors.topMargin: root.shadowYOffset
        radius: card.radius
        color: root.shadowColor
        visible: root.shadowEnabled

        layer.enabled: root.shadowEnabled
        layer.effect: MultiEffect {
            blurEnabled: true
            blur: 1.0
            blurMax: root.shadowBlur
            shadowEnabled: false
        }
    }

    // ---------------------------------------------------------------- 卡片本体
    Rectangle {
        id: card
        anchors.fill: parent
        radius: root.radius
        color: root.cardColor
        border.width: 1
        border.color: root.borderColor
        clip: true

        Column {
            id: contentColumn
            anchors.fill: parent
            anchors.margins: root.padding
            spacing: root.contentSpacing

            // ---- 标题
            Text {
                id: titleText
                text: root.title
                color: root.titleColor
                font.pixelSize: root.titleFontSize
                font.bold: true
                elide: Text.ElideRight
                width: parent.width
            }

            // ---- 副标题（可选）
            Text {
                id: subtitleText
                text: root.subtitle
                color: root.subtitleColor
                font.pixelSize: root.subtitleFontSize
                wrapMode: Text.Wrap
                width: parent.width
                visible: root.subtitle !== ""
            }

            // ---- 按钮（右对齐）
            NovaButton {
                id: actionButton
                text: root.buttonText
                visible: root.showButton
                anchors.right: parent.right
                onClicked: root.buttonClicked()
            }
        }
    }

    // 内容高度自适应：把 Column 的隐式高度回传给 root
    implicitHeight: contentColumn.implicitHeight + padding * 2
}
