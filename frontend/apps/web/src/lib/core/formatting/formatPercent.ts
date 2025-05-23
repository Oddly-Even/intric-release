export function formatPercent(number: number, decimals = 2, base = 1) {
  if (decimals < 0) {
    throw new Error("decimals must be >= 0");
  }

  if (isNaN(number)) {
    number = 0;
  }

  const calc = (number * 100) / base;
  return calc.toFixed(decimals) + "%";
}
