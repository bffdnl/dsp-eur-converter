
# SDR to EUR Converter

### Special Drawing Rights to Euro Conversion Using Official IMF Exchange Rates

A free, open-source, web-based tool for converting **Special Drawing Rights (SDR)** into euros (EUR), using exchange rate data published by the **International Monetary Fund (IMF)**.

Designed for professionals, financial institutions, administrative offices, and anyone requiring accurate, transparent, and easily accessible SDR-to-EUR conversions, including historical exchange rates.

---

## 🌐 Try the Converter

**[Launch the SDR to EUR Converter](https://bffdnl.github.io/dsp-eur-converter/)**

Access the application directly from your browser on desktop computers, tablets, and smartphones. No installation or registration is required.

---

## ✨ Features

- **Instant Conversion:** Convert any SDR amount into euros using official IMF exchange rate data.
- **Historical Exchange Rates:** Select any date from January 2, 2001, onwards.
- **Nearest Available Rate:** If no IMF rate is available for the selected date (e.g., weekends or holidays), the converter automatically uses the closest available valuation date.
- **Automatic Updates:** Exchange rate data is periodically refreshed through GitHub Actions.
- **Historical Currency Basket Support:** Handles both the four-currency SDR basket used before October 2016 and the five-currency basket introduced with the inclusion of the Chinese renminbi.
- **Browser-Based Access:** No installation, registration, or additional software required.
- **Open Source:** The source code is publicly available for transparency, review, and contributions.

---

## 📊 Data Source and Methodology

The converter uses SDR valuation data published by the **International Monetary Fund (IMF)**.

**Official data source:** [IMF – SDR Valuation](https://www.imf.org/external/np/fin/data/rms_sdrv.aspx)

The SDR-to-EUR exchange rate is calculated using the SDR value expressed in US dollars and the corresponding US dollar exchange rate of the euro.

### Conversion Formula

```text
SDR value in EUR = SDR amount × (USD per SDR / USD per EUR)
```

Where:

- **USD per SDR:** The US dollar value of one Special Drawing Right.
- **USD per EUR:** The US dollar value of one euro.

Historical conversions use the IMF valuation applicable to the selected date or, when unavailable, the nearest available valuation date.

The application supports historical SDR currency basket changes, including the addition of the Chinese renminbi on October 1, 2016.

---

## 🔄 Automatic Data Updates

Exchange rate data is periodically retrieved from the IMF and processed using Python scripts and **GitHub Actions**.

The automated workflow:

1. Retrieves the latest available SDR valuation data.
2. Processes historical exchange rates.
3. Updates the data files used by the converter.
4. Deploys the updated website through GitHub Pages.

The application automatically selects the nearest available IMF valuation when an exact date is unavailable.

---

## 🛠️ Technologies

- **HTML5** — Application structure
- **CSS3** — Responsive interface
- **JavaScript** — Conversion logic
- **Python** — IMF data retrieval and processing
- **GitHub Actions** — Automated updates and deployment
- **GitHub Pages** — Free web hosting

---

## 📅 Historical Data Coverage

Historical SDR-to-EUR conversions are supported from **January 2, 2001**, onwards.

The converter handles two different SDR currency basket configurations:

| Period | SDR Currency Basket |
|--------|---------------------|
| Jan 2, 2001 – Sep 30, 2016 | USD, EUR, JPY, GBP |
| From Oct 1, 2016 | USD, EUR, CNY, JPY, GBP |

When an IMF valuation is unavailable for a selected date, the application uses the nearest available observation and displays the effective valuation date.

---

## ⚠️ Disclaimer

This is an **independent, unofficial project** and is **not affiliated with, endorsed by, sponsored by, or maintained by the International Monetary Fund (IMF)**.

Although the converter uses data published by the IMF, users should independently verify the applicable valuation date and exchange rates against the official source when performing financial, contractual, administrative, or legal calculations.

The software is provided for informational purposes **"as is"**, without any warranty of accuracy, completeness, fitness for a particular purpose, or uninterrupted availability.

All references to the IMF and its trademarks belong to their respective owners.

---

## 🔗 Useful Links

- **[Live Converter](https://bffdnl.github.io/dsp-eur-converter/)**
- **[GitHub Repository](https://github.com/bffdnl/dsp-eur-converter)**
- **[Official IMF SDR Valuation Data](https://www.imf.org/external/np/fin/data/rms_sdrv.aspx)**

---

## 📄 License

The source code is publicly available.
