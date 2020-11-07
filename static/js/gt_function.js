// 初始化图
init_graph = function (graph) {
    graph = JSON.parse(graph);

    //给节点的属性进行操作
    graph.nodes.forEach(function (node) {
        node.itemStyle = null;
        node.symbolSize = 20;  // 节点的大小
        node.category = node.category;
        node.draggable = true;  // 设置节点可以拖拽
    });
    return graph;
};

// 初始化option
init_option = function (graph) {
    var option;
    var categories = [];
    categories[0] = {
        name: '进行行为0的节点',
        itemStyle: {
            color: '#009688',
            opacity: 1, //不透明度
            fontSize: 10
        },
        label: {
            fontSize: 15,
            opacity:1,
            color: '#000000'
        },
    }
    categories[1] = {
        name: '进行行为1的节点',
        itemStyle: {
            color: '#ff0000',
            opacity: 1, //不透明度
        },
        label: {
            fontSize: 20,
            opacity:1,
            color:'#000000'
        },

    };
    //设置要生成的图的相关属性
    option = {
        // 图表标题
        title: {
            text: '',
            subtext: '',
            top: 'top',
            left: 'left'
        },

        // 提示框
        tooltip: {},

        // 图例
        legend: [{
            // selectedMode: 'single',
            data: categories.map(function (a) {
                return a.name;
            })
        }],
        animationDuration: 1500,  // 动画持续时间
        animationEasingUpdate: 'quinticInOut',
        series: [
            {
                name: 'Les Miserables',
                type: 'graph',
                layout: 'none',
                //下面三项分别设置节点数据，边数据，种类数据
                data: graph.nodes,
                links: graph.links,
                categories: categories,
                roam: true,
                animation: false,
                focusNodeAdjacency: true,
                itemStyle: {
                    normal: {
                        borderColor: '#fff',
                        borderWidth: 1,
                        shadowBlur: 10,
                        shadowColor: 'rgba(0, 0, 0, 0.3)'
                    }
                },
                label: {
                    position: 'right',
                    formatter: '{b}'
                },
                lineStyle: {
                    color: 'rgba(0, 0, 0, 0.7)',
                    curveness: 0.3
                },
                emphasis: {
                    lineStyle: {
                        width: 10
                    }
                },
                force: {
                    repulsion: 270
                }
            }
        ]
    };
    return option;
}
