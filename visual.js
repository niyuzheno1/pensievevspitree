legend = svg => {
  const g = svg
      .attr("transform", `translate(${width},0)`)
      .attr("text-anchor", "end")
      .attr("font-family", "sans-serif")
      .attr("font-size", 10)
    .selectAll("g")
    .data(color.domain().slice().reverse())
    .join("g")
      .attr("transform", (d, i) => `translate(0,${i * 20})`);

  g.append("rect")
      .attr("x", -19)
      .attr("width", 19)
      .attr("height", 19)
      .attr("fill", color);

  g.append("text")
      .attr("x", -24)
      .attr("y", 9.5)
      .attr("dy", "0.35em")
      .attr("font-size","x-large")
      .text(d => d);
}


x0 = d3.scaleBand()
    .domain(data.map(d => d[groupKey]))
    .rangeRound([margin.left, width - margin.right])
    .paddingInner(0.1)

x1 = d3.scaleBand()
    .domain(keys)
    .rangeRound([0, x0.bandwidth()])
    .padding(0.05)

y = d3.scaleLinear()
    .domain([0, d3.max(data, d => d3.max(keys, key => d[key]))]).nice()
    .rangeRound([height - margin.bottom, margin.top])

color = d3.scaleOrdinal()
    .range(["#a85432","#7074b8","#39ff2b","#7b6888", "#6b486b", "#a05d56", "#d0743c", "#ff8c00"])

xAxis = g => g
    .attr("transform", `translate(0,${height - margin.bottom})`)
    .call(d3.axisBottom(x0).tickSizeOuter(0))
    .call(g => g.select(".domain").remove())
    .attr("font-size", "x-large")


yAxis = g => g
    .attr("transform", `translate(${margin.left},0)`)
    .call(d3.axisLeft(y).ticks(null, "s"))
    .call(g => g.select(".domain").remove())
    .attr("font-size", "larger")
    .call(g => g.select(".tick:last-of-type text").clone()
        .attr("x", 3)
        .attr("text-anchor", "start")
        .attr("font-weight", "bold")
        .attr("font-size", "larger")
         .text(data.y))

data = Object.assign(d3.csvParse(await FileAttachment("stats11.csv").text(), d3.autoType), {x: "metric", y: "Value"})

groupKey = data.columns[0]

keys = data.columns.slice(1)

margin = ({top: 10, right: 10, bottom: 20, left: 40})

height = 500

d3 = require("d3@5")
