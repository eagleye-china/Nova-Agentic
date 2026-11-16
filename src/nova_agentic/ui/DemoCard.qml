// DemoCard.qml -- NovaCard 使用示例
import QtQuick
import QtQuick.Window

Window {
    id: win
    width: 760
    height: 460
    visible: true
    title: "NovaCard 组件演示"
    color: "#F5F7FA"

    // 卡片 1：最简用法
    NovaCard {
        id: simpleCard
        x: 40
        y: 40
        width: 320
        title: "极简卡片"
        subtitle: "只填 title / subtitle / buttonText 就能用"
        buttonText: "知道了"

        onButtonClicked: console.log("✅ 简单卡片按钮被点击")
    }

    // 卡片 2：自定义配色 + 关闭按钮 + 插入自定义内容
    NovaCard {
        id: customCard
        x: 400
        y: 40
        width: 320
        radius: 18
        title: "自定义样式"
        subtitle: "改了圆角、阴影偏移和主题色"
        cardColor: "#111827"
        titleColor: "#F9FAFB"
        subtitleColor: "#9CA3AF"
        borderColor: "#374151"
        shadowBlur: 36
        shadowYOffset: 12
        buttonText: "运行"
        showButton: true

        // 往默认插槽里塞一个进度条
        Rectangle {
            width: parent.width
            height: 6
            radius: 3
            color: "#374151"

            Rectangle {
                width: parent.width * 0.66
                height: parent.height
                radius: 3
                color: "#3B82F6"
            }
        }

        onButtonClicked: console.log("✅ 深色卡片按钮被点击")
    }

    // 卡片 3：隐藏按钮，纯展示
    NovaCard {
        x: 40
        y: 260
        width: 680
        title: "纯展示卡片"
        subtitle: "showButton: false，宽度自适应撑满"
        showButton: false
    }

    Component.onCompleted: console.log("🎉 卡片组件加载完成")
}
