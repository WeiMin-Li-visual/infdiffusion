init_graph = function(graph, flag=true){
    graph = JSON.parse(graph);

    //给节点的属性进行操作
    graph.nodes.forEach(function (node) {
        node.itemStyle = null;
        node.symbolSize = 15;
        // node.value = node.symbolSize;
        //if(flag == true)
            //node.category = node.attributes.modularity_class;
        node.draggable = true;
    });
    return graph;
};

init_option = function(graph){
    var option;
    var categories = [];
    // categories[0] = {
    //         name: '普通节点',
    //         itemStyle: {
    //             color: '#2f4554',
    //             opacity: 0.9, //不透明度
    //         }
    //     }
        categories[0] = {
            name: '观测节点',
            itemStyle: {
                color: '#009688',
                opacity: 1, //不透明度
            },
            label: {
                fontSize: 20,
            },

        }
        categories[1] = {
            name: '源节点',
            itemStyle: {
                color: '#FF0000',
                opacity: 1, //不透明度
            },
            label: {
                fontSize: 25,
            },

        }
        categories[2] = {
            name: '感染节点',
            itemStyle: {
                color: '#EE82EE',
                opacity: 1, //不透明度
            },
            label: {
                fontSize: 15,
            },

        }
         categories[3] = {
            name: '预测的源节点',
            itemStyle: {
                color: '#9400D3',
                opacity: 1, //不透明度
            },
            label: {
                fontSize: 30,
            },

        }
         categories[4] = {
            name: '社区1',
            itemStyle: {
                color: '#4169E1',
                opacity: 1, //不透明度
            },
            label: {
                fontSize: 15,
            },

        }
         categories[5] = {
            name: '社区2',
            itemStyle: {
                color: '#00FF7F',
                opacity: 1, //不透明度
            },
            label: {
                fontSize: 15,
            },

        }
         categories[6] = {
            name: '社区3',
            itemStyle: {
                color: '#DAA520',
                opacity: 1, //不透明度
            },
            label: {
                fontSize: 15,
            },

        }
         categories[7] = {
            name: '社区4',
            itemStyle: {
                color: '#00BFFF',
                opacity: 1, //不透明度
            },
            label: {
                fontSize: 15,
            },

        };
    //设置要生成的图的相关属性
    option = {
        title: {
            text: '',
            subtext: '',
            top: 'top',
            left: 'left'
        },

       // grid:{
       //      left:'8%',
       //      right :'0',
       //      bottom :'1%'
       //
       // },
        tooltip: {},
        legend: [{
            // selectedMode: 'single',
            data: categories.map(function (a) {
                return a.name;
            })
        }],
        animationDuration: 1500,
        animationEasingUpdate: 'quinticInOut',

        series: [
            {
                name: '节点id:感染时间',
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
                    //color: 'rgba(0, 0, 0, 0.7)',
                    color: 'source',
                    curveness: 0.3,
                    width: 0.7
                },
                emphasis: {
                    lineStyle: {
                        width: 5
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
