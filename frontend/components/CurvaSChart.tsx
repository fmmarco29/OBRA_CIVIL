"use client";
import React from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

interface ChartProps {
  wbs: any[];
  actualDay: number;
  actualCost: number;
  ev: number;
}

export default function CurvaSChart({ wbs, actualDay, actualCost, ev }: ChartProps) {
  const points = [];
  for (let d = 1; d <= 730; d += 10) {
    let pv = 0;
    wbs.forEach((row) => {
      const start = row.Start_Day;
      const dur = row.Duration;
      const cost = row.Cost;
      const end = start + dur - 1;
      if (d > end) pv += cost;
      else if (d >= start) pv += ((d - start + 1) / dur) * cost;
    });

    const point: any = { day: d, "Planned Value": pv };
    if (d <= actualDay) {
      const fraction = d / actualDay;
      point["Actual Cost"] = actualCost * fraction;
      point["Earned Value"] = ev * fraction;
    }
    points.push(point);
  }

  return (
    <div className="w-full h-80">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={points} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis dataKey="day" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" />
          <Tooltip contentStyle={{ backgroundColor: "#14182b", border: "1px solid rgba(255,255,255,0.1)" }} />
          <Legend />
          <Line type="monotone" dataKey="Planned Value" stroke="#3b82f6" strokeWidth={3} dot={false} />
          <Line type="monotone" dataKey="Earned Value" stroke="#34d399" strokeWidth={3} strokeDasharray="5 5" dot={false} />
          <Line type="monotone" dataKey="Actual Cost" stroke="#ef4444" strokeWidth={3} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
