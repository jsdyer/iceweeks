import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {weekDates, season, weekIndex, match} from "../web/model.mjs";
const data = JSON.parse(readFileSync(new URL("../web/data/index.json",import.meta.url)));
test("Winter boundaries cross January and include leap years",()=>{
 assert.equal(season("2023-12-01"),2023);
 assert.equal(season("2024-02-29"),2023);
 assert.equal(weekIndex("2024-02-29"),12);
 assert.deepEqual(weekDates(2023,21),["2024-04-26","2024-04-30"]);
});
test("Every issue falls in its own selectable bin and each PDF is published",()=>{
 assert.equal(data.charts.length,data.count);
 for (const c of data.charts) {
   assert.ok(match(data.charts,season(c.date),weekIndex(c.date)).includes(c));
   assert.match(c.pdf,/^https:\/\/www\.polarview\.aq\//);
 }
 assert.deepEqual(match(data.charts,1990,1),[]);
});
