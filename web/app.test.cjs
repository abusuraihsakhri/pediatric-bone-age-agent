"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const { compareBoneAges } = require("./app.js");

test("positive, negative and equal differences", function () {
  assert.equal(compareBoneAges(120, 132, "Greulich-Pyle").difference_months, 12);
  assert.equal(compareBoneAges(120, 108).direction, "delayed");
  assert.equal(compareBoneAges(120, 120).direction, "equal");
  assert.equal(compareBoneAges(120.25, 120.5).difference_months, 0.25);
});
test("finite and bounded ages", function () {
  for (const invalid of [NaN, Infinity, -1, 241, "120", null, undefined]) {
    assert.throws(function () { compareBoneAges(invalid, 120); }, RangeError);
    assert.throws(function () { compareBoneAges(120, invalid); }, RangeError);
  }
});
test("unsupported method is rejected", function () {
  assert.throws(function () { compareBoneAges(120, 120, "TW99"); }, RangeError);
});
test("boundary ages", function () {
  assert.equal(compareBoneAges(0, 240).difference_months, 240);
});
