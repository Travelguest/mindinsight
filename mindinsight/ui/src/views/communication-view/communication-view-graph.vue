<template>
  <div class="communication-container">
    <div class="communication-sub-title">
      <svg class="subtitle-svg" width="90%" height="100%">
        <defs>
          <linearGradient
            id="myLinearGradient1"
            x1="0%"
            y1="0%"
            x2="100%"
            y2="0%"
            spreadMethod="pad"
          >
            <stop offset="0%" stop-color="#fbe7d5" stop-opacity="1" />
            <stop offset="100%" stop-color="#e6882e" stop-opacity="1" />
          </linearGradient>
        </defs>
        <g class="subtitle-container">
          <g id="subtitle-line1">
            <text x="0" y="15">Node-link graph:</text>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="-2.75 0 28 13">
              <g transform="scale(0.25)">
                <circle class="cls-1" cx="3.5" cy="6.5" r="3" />
                <circle class="cls-1" cx="21.5" cy="6.5" r="6" />
                <line class="cls-2" x1="3.5" y1="3.5" x2="21.5" y2="0.5" />
                <line class="cls-2" x1="3.5" y1="9.5" x2="21.5" y2="12.5" />
              </g>
            </svg>
            <text x="155" y="15">The total communication cost</text>
          </g>
          <g id="subtitle-line2">
            <text x="0" y="40">0</text>
            <rect
              x="15"
              y="30"
              width="65"
              height="10"
              fill="url(#myLinearGradient1)"
            ></rect>
            <text x="85" y="40">1</text>
            <text x="100" y="40">The Proportion of communication time</text>
          </g>
          <g id="subtitle-line3">
            <text x="0" y="65">Matrix:</text>
            <rect x="50" y="55" width="10" height="10" fill="#f6b59a"></rect>
            <text x="63" y="65">Communication time</text>
            <rect x="200" y="55" width="10" height="10" fill="#a8d2e5"></rect>
            <text x="213" y="65">Traffic</text>
            <rect x="260" y="55" width="10" height="10" fill="#378dc0"></rect>
            <text x="273" y="65">BandWidth</text>
          </g>
        </g>
      </svg>
    </div>
    <div class="communication-graph-box">
      <div id="networkPlot"></div>
    </div>
  </div>
</template>

<style>
.communication-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.communication-sub-title {
  width: 100%;
  height: 75px;
  padding-top: 5px;
  margin-left: 16px;
}
.communication-view {
  height: 100%;
}

#networkPlot {
  position: relative;
  width: 100%;
  height: 100%;
}
.communication-graph-box {
  /* position: relative; */
  height: 70%;
  width: 100%;
  /* flex-grow: 1; */
}
.el-icon-magic-stick {
  position: absolute;
  top: 0;
  right: 5%;
  z-index: 999;
}

.lasso path {
  stroke: rgb(80, 80, 80);
  stroke-width: 2px;
}

.lasso .drawn {
  fill-opacity: 0.05;
}

.lasso .loop_close {
  fill: none;
  stroke-dasharray: 4, 4;
}

.lasso .origin {
  fill: #3399ff;
  fill-opacity: 0.5;
}
.cls-1,
.cls-2 {
  fill: none;
  stroke: #cbcbcb;
  stroke-miterlimit: 10;
}
.cls-2 {
  stroke-dasharray: 2;
}
</style>
<script>
import {
  device_node,
  communicate_link,
} from "@/js/communicate-view/build-graph.js";
import requestService from "@/services/request-service";
import * as vis from "vis";
import * as echarts from "echarts/core";
import * as d3 from "d3";
import { Graph } from "@/js/communicate-view/graph.js";
import { Paths } from "@/js/communicate-view/path.js";
import { Lasso } from "@/js/communicate-view/lasso.js";
export default {
  data() {
    return {
      stepNum: 1,
      communicateNodes: {},
      communicateEdges: {},
      communicateOps: {},
      communicateGraphData: {},

      linecharOption: null,
      linechart: null,

      opNameMap: null,
    };
  },
  mounted() {
    // this.initSubtitle();
    this.initGraph();
  },
  watch: {
    "$store.state.stepNum": function (val) {
      this.stepNum = val;
      this.renderNetwork();
    },
    "$store.state.selectCommunicateOpnode": function (val) {
      this.recieveOpnode(val);
    },
    "$store.state.opNameMap": function (val) {
      console.log("收到opNameMap", val);
      this.opNameMap = val;
    },
  },

  methods: {
    async initGraph() {
      await this.fetchData();
      //发送communicateNodes 给LineChart
      this.$store.commit("setCommunicateNodes", this.communicateNodes);
      this.$store.commit("setCommunicationData", this.communicateGraphData);

      // this.generateGraph();
      this.renderNetwork();
      // this.generateCanvas();
    },
    async fetchData() {
      const res = (await requestService.getCommunicationGraph()).data;
      this.communicateGraphData = res;
      for (var device in this.communicateGraphData) {
        for (var i in this.communicateGraphData[device]) {
          var step_info = this.communicateGraphData[device][i];
          var new_node = Object.create(device_node);
          new_node.name = device;
          new_node.communication_cost = step_info["communication_cost"];
          new_node.wait_cost = step_info["wait_cost"];
          new_node.opNodes = step_info["communication_operator_cost"];
          if (!this.communicateNodes.hasOwnProperty(step_info["step_num"])) {
            this.communicateNodes[step_info["step_num"]] = [];
          }
          this.communicateNodes[step_info["step_num"]].push(new_node);
          var link_info = step_info["link_info"];
          if (!this.communicateEdges.hasOwnProperty(step_info["step_num"])) {
            this.communicateEdges[step_info["step_num"]] = [];
          }
          if (!this.communicateOps.hasOwnProperty(step_info["step_num"])) {
            this.communicateOps[step_info["step_num"]] = {};
          }

          for (var link in link_info) {
            for (var type in link_info[link]) {
              var new_link = Object.create(communicate_link);
              var node_pair = link.split("-");
              new_link.source = node_pair[0];
              new_link.target = node_pair[1];

              if (
                !this.communicateGraphData.hasOwnProperty(
                  "device" + new_link.source
                ) ||
                !this.communicateGraphData.hasOwnProperty(
                  "device" + new_link.target
                )
              ) {
                continue;
              }
              new_link.type = type;
              new_link.value = link_info[link][type][0];
              new_link.communication_duration = link_info[link][type][0];
              new_link.traffic = link_info[link][type][1];
              new_link.bandWidth = link_info[link][type][2];
              // console.log(step, this.maxBarValue[step][0]);
              // this.maxBarValue[step].duration = Math.max(
              //   this.maxBarValue[step].duration,
              //   link_info[link][type][0]
              // );
              // this.maxBarValue[step].traffic = Math.max(
              //   this.maxBarValue[step].traffic,
              //   link_info[link][type][1]
              // );
              this.communicateEdges[step_info["step_num"]].push(new_link);
            }
          }

          var op_info = step_info["communication_operator_cost"];

          var step = step_info["step_num"];
          for (var op_name in op_info) {
            // console.log(op_name, op_info[op_name][3]);
            for (var link in op_info[op_name][3]) {
              if (!this.communicateOps[step].hasOwnProperty(link)) {
                this.communicateOps[step][link] = [];
              }
              for (var link_type in op_info[op_name][3][link]) {
                var duration = op_info[op_name][3][link][link_type][0];
                var traffic = op_info[op_name][3][link][link_type][1];
                var bandWidth = op_info[op_name][3][link][link_type][2];

                // this.maxBarValue = this.maxBarValue[step_info["step_num"]]
                // this.maxBarValue = Math.max(traffic, this.maxBarValue);
                // this.maxBarValue = Math.max(traffic, this.maxBarValue);
                this.communicateOps[step][link].push({
                  device: device,
                  op_name: op_name,
                  duration: duration,
                  traffic: traffic,
                  bandWidth: bandWidth,
                });
              }
            }
          }
        }
      }
    },
    renderNetwork() {
      // network data
      // console.log(this.communicateOps);
      if (!this.communicateNodes[this.stepNum]) return;
      var dataLink = [];
      var dataNode = [];

      this.communicateNodes[this.stepNum].forEach(function (d) {
        dataNode.push({
          id: d.name,
          label: d.name.replace("device", ""),
          c_cost: d.communication_cost,
          w_cost: d.wait_cost,
        });
      });

      // console.log(this.communicateEdges[this.stepNum]);
      this.communicateEdges[this.stepNum].forEach((d) => {
        var op_duration = [],
          op_traffic = [],
          op_bandWidth = [];
        var link_str = d.source + "-" + d.target;
        var op_info = this.communicateOps[this.stepNum][link_str];
        op_info.forEach((i) => {
          op_duration.push({
            name: i["op_name"],
            value: i["duration"],
            device: i["device"],
          });
          op_traffic.push({
            name: i["op_name"],
            value: i["traffic"],
            device: i["device"],
          });
          op_bandWidth.push({
            name: i["op_name"],
            value: i["bandWidth"],
            device: i["device"],
          });
        });
        dataLink.push({
          source: "device" + d.source,
          target: "device" + d.target,
          weight: d.value,
          link_type: d.type,
          communication_duration: d.communication_duration,
          traffic: d.traffic,
          bandWidth: d.bandWidth,
          op_duration: op_duration.sort((a, b) => a.value - b.value),
          op_traffic: op_traffic.sort((a, b) => a.value - b.value),
          op_bandWidth: op_bandWidth.sort((a, b) => a.value - b.value),
        });
      });

      var width = document.getElementById("networkPlot").clientWidth;
      var height = document.getElementById("networkPlot").clientHeight;

      d3.selectAll("#networkPlot>*").remove();
      var svg = d3
        .select("#networkPlot")
        .append("svg")
        .attr("id", "mainsvg")
        .attr("width", width)
        .attr("height", height);

      d3.selectAll("#matrix > *").remove();
      d3.selectAll("#force > *").remove();
      d3.selectAll("#path > *").remove();

      var matrix_layer = svg.append("g").attr("id", "matrix");
      var force_layer = svg.append("g").attr("id", "force");
      var path_layer = svg.append("g").attr("id", "path");
      // console.log(this.maxBarValue);
      window.communicategraph = new Graph(width, height, this);
      window.communicategraph.init(dataLink, dataNode);
    },

    setSelectErrorOp(op) {
      var opname = this.transformOpId2Name(op.device, op.name);
      if (opname) this.$store.commit("setSelectErrorOp", opname);

      // this.$store.commit("setSelectOpname", opname.split("_"));
    },

    transformOpId2Name(opDevice, opname) {
      var opType = opname.split("_")[0];
      var opId = Number(opname.split("_")[1]);
      var resName = undefined;
      // if (opType == "allReduce") opType = "AllReduce";
      // else if (opType == "send") opType = "Send";
      // else if (opType == "receive") opType = "Receive";
      // else {
      //   console.log("不能在opNameMap中找到类型", opType);
      //   return resName;
      // }
      var newOpType = undefined;
      for (var i = 0; i < Object.keys(this.opNameMap[opDevice]).length; i++) {
        if (
          opType.toLowerCase() ==
          Object.keys(this.opNameMap[opDevice])[i].toLowerCase()
        ) {
          newOpType = Object.keys(this.opNameMap[opDevice])[i];
        }
      }
      if (newOpType) {
        var deviceOpMap = this.opNameMap[opDevice][newOpType];

        if (deviceOpMap[opId - 1]) {
          resName = deviceOpMap[opId - 1];
          console.log("在opNameMap中对应算子名", deviceOpMap[opId - 1]);
        } else console.log("不能在opNameMap中找到该算子", opDevice, opname);
      } else {
        console.log("不能在opNameMap中找到类型", opType);
      }

      return resName;
    },

    recieveOpnode(opName) {
      if (this.opNameMap == null) {
        console.log("未收到opNameMap，请刷新页面重试");
      }
      if (opName != null) {
        console.log(
          this.opNameMap,
          this.communicateNodes[this.stepNum],
          opName
        );
        var nameList = opName.split("/");
        var name = nameList[nameList.length - 1];
        this.$store.commit("setSelectErrorOp", name);
        nameList = name.split("-");
        var type = nameList[0];

        var opNodeList = [];
        Object.keys(this.opNameMap).forEach((device) => {
          // console.log(device, this.opNameMap[device][type]);
          var opIndex = this.opNameMap[device][type].indexOf(name);
          if (opIndex > -1) {
            // console.log(device, opIndex, name);
            opNodeList.push({ device: device, type: type, index: opIndex + 1 });
          }
        });

        var matrixOpData = [];

        opNodeList.forEach((opInfo) => {
          var targetName = opInfo.type + "_" + opInfo.index;
          targetName = targetName.toLowerCase();
          // console.log(nodeInfo.device, this.communicateNodes[this.stepNum]);
          this.communicateNodes[this.stepNum]
            .filter((d) => d.name == opInfo.device)
            .forEach((nodeData) => {
              // console.log(nodeData.opNodes);
              for (var i = 0; i < Object.keys(nodeData.opNodes).length; i++) {
                if (
                  Object.keys(nodeData.opNodes)
                    [i].toLowerCase()
                    .startsWith(targetName)
                ) {
                  var findData =
                    nodeData.opNodes[Object.keys(nodeData.opNodes)[i]];

                  if (findData[3] != {}) {
                    // console.log(findData[3]);
                    Object.keys(findData[3]).forEach((link) => {
                      // console.log(link);
                      var linkList = link.split("-");
                      var link_type = Object.keys(findData[3][link])[0];
                      matrixOpData.push({
                        source: "device" + linkList[0],
                        target: "device" + linkList[1],
                        opValue: findData[3][link][link_type],
                      });
                    });
                  }
                  break;
                }
              }
            });
        });
        window.communicategraph.showOpNode(matrixOpData);
        console.log(matrixOpData);
      }
    },
  },
};
</script>
