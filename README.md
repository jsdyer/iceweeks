# Ice Weeks

[Compare East Coast ice charts](https://coolcode.ca/iceweeks/)

Compare weekly East Coast total ice concentration charts issued by the Canadian Ice Service. Choose two winters and move through the same week of each. Open a chart PDF for the full-resolution map and legend.

<!-- coolcode:guide -->
Choose winters 2025–2026 and 2024–2025 and move to week 12 to compare the charts issued February 16, 2026 and February 17, 2025. An empty panel means the archive index has no chart in that week.
<!-- /coolcode:guide -->

## Chart source and coverage

The [Ice Logistics Portal](https://www.icelogistics.info/ice-charts?iceChartProductId=2213), maintained for the International Ice Charting Working Group, indexes the Canadian Ice Service East Coast concentration product (2213). Preview images and PDF files are served by the portal’s Polar View archive. Consult the [Canadian Ice Service archive guide](https://www.canada.ca/en/environment-climate-change/services/ice-forecasts-observations/latest-conditions/archive-overview/information-about-data.html) for information about Canadian ice analyses.

The index checks December through April from winter 2023–2024 onward. At release, it contains 55 chart dates from February 12, 2024 to April 27, 2026. Weekly bins start on December 1, with the last bin ending on April 30. The first bin always covers December 1–7. Leap years shift the later date labels by a day. Each panel shows the actual issue date, and all matching chart links appear if a bin has several issues. Empty weeks are retained. The provincial coastline, not a user-selected location, provides the reference for visual comparison. A chart describes conditions analyzed for its issue date and belongs to a historical series.

The displayed retrieval date refers to the chart index. Opening the tool loads available preview images directly from Polar View, and opening a PDF contacts the same provider. The app stores no user selections.

## Maintenance

A weekly GitHub Actions job queries the catalogue in monthly windows, checks the series, provider, asset hosts, chart count and previously indexed dates, then publishes the updated snapshot. Failed catalogue checks preserve the published index. Run `python3 scripts/refresh.py` to refresh locally. If the upstream site changes its product catalogue format, review the parser before replacing existing data. Keep tool.json and the marked guide above current with the scope of the app.

Run `node --test tests/*.test.mjs`, `python3 -m unittest discover -s tests -v`, and `python3 scripts/build.py`. Serve dist with `python3 -m http.server 8000 --directory dist`. CI exercises week and season selection, missing images and mobile layout in Chromium.
