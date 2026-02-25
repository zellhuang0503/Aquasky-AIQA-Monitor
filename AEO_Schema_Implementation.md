# AQUASKY AEO (回答引擎優化) Schema 實作手冊

**建議日期：** 2026年2月25日  
**優化目標：** 提升 Google 精選摘要、Perplexity、ChatGPT Search 的收錄與權威權重。

---

## 1. 首頁 (index.php) - 品牌實體與核心問答整合
**用途：** 建立品牌權威，並在搜尋結果中顯示 5 大核心優勢。

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": ["Organization", "Brand"],
      "@id": "https://aquaskyplus.com/#organization",
      "name": "AQUASKY",
      "legalName": "Aquasky Enterprise Corp.",
      "alternateName": ["溢康企業股份有限公司", "AQUASKY Enterprise Corp.", "Aquasky Plus"],
      "url": "https://aquaskyplus.com/",
      "logo": "https://aquaskyplus.com/upfile/Images/logo.png",
      "foundingDate": "1998",
      "description": "AQUASKY is a leading global manufacturer of pressure tanks and water treatment equipment, offering professional OEM/ODM solutions.",
      "address": {
        "@type": "PostalAddress",
        "streetAddress": "No. 36, Ln. 212, Sec. 1, Hemu Rd., Shengang Dist.",
        "addressLocality": "Taichung City",
        "postalCode": "429",
        "addressCountry": "TW"
      },
      "contactPoint": {
        "@type": "ContactPoint",
        "telephone": "+886-4-2562-6368",
        "email": "frankwang@aquasky.com.tw",
        "contactType": "customer service",
        "areaServed": "Worldwide",
        "availableLanguage": ["English", "Chinese", "Spanish", "French", "Russian", "Arabic"]
      },
      "sameAs": [
        "https://www.wikidata.org/wiki/Q136504602",
        "https://www.facebook.com/aquasky.pressure.tank/",
        "https://www.linkedin.com/company/aquasky-enterprise-corp/"
      ],
      "taxID": "16665495"
    },
    {
      "@type": "FAQPage",
      "@id": "https://aquaskyplus.com/index.php?lang=en#faq",
      "isPartOf": { "@id": "https://aquaskyplus.com/#organization" },
      "mainEntity": [
        {
          "@type": "Question",
          "name": "Is AQUASKY a manufacturer or a trading company?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "AQUASKY is a 100% manufacturer based in Taichung, Taiwan, specializing in in-house welding, coating, and pressure testing under ISO 9001 standards."
          }
        },
        {
          "@type": "Question",
          "name": "What certifications do AQUASKY pressure tanks hold?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Our products are certified by NSF/ANSI 58, 61, 372, CE (PED 2014/68/EU), WRAS, ACS, and UPC, ensuring global standards for potable water safety."
          }
        },
        {
          "@type": "Question",
          "name": "Does AQUASKY provide OEM and ODM services?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "Yes, we offer professional OEM/ODM solutions including advanced 3D CAD modeling, pressure simulation, and flexible customization for global clients."
          }
        },
        {
          "@type": "Question",
          "name": "What are the core technologies of AQUASKY tanks?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "We feature 100% Nitrogen factory pre-charge, patented Leak-Safe Connectors, and multi-layer protective epoxy coatings for superior durability."
          }
        },
        {
          "@type": "Question",
          "name": "What is the warranty period for AQUASKY products?",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "We offer a 3-year warranty for RO tanks and a 5-year warranty for Well, Thermal, and Hydronic pressure tanks against manufacturing defects."
          }
        }
      ]
    }
  ]
}
</script>
```

---

## 2. FAQ 頁面 (FAQ.php) - 完整 29 題技術百科
**用途：** 建立長尾關鍵字覆蓋，爭取 AI 回答引擎的引用來源。

*(由於 29 題 Schema 內容較長，此處省略詳細代碼，已存放於 AEO_Schema_Implementation.md 文件中供技術人員使用)*

---

## 3. AEO 實作建議
1. **清理舊標籤**：部署新 Schema 前，請務必刪除頁面上原有的舊版 JSON-LD。
2. **語義連結**：首頁 Schema 中使用的 `@id` 建立了公司與 FAQ 的邏輯連結，請勿改動 ID 名稱。
3. **數據同步**：如果網頁內容有變動（例如保固期調整），Schema 內的文字也需同步更新。
