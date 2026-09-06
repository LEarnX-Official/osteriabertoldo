/* Osteria il Bertoldo — bilingual content
   IT is primary; EN is the toggle.
   ⚠️ MENU DISHES AND PRICES ARE PLACEHOLDER — replace with the real menu.
   Every placeholder item carries `placeholder: true`. */

const CONTENT = {
  it: {
    langLabel: "IT",
    nav: { home: "Home", storia: "Storia", menu: "Menù", galleria: "Galleria", contatti: "Contatti" },
    hero: {
      eyebrow: "Verona · dal 1988",
      title: "Osteria<br>il Bertoldo",
      sub: "Ristorante di qualità nel cuore del centro storico",
      ctaBook: "Prenota un tavolo",
      ctaMenu: "Scopri il menù",
      scroll: "Scorri"
    },
    storia: {
      eyebrow: "La nostra storia",
      title: "Dal 1988 nel cuore di Verona",
      body: [
        "Se desideri vivere un'esperienza culinaria diversa dall'ordinario grazie a piatti di altissima qualità, vieni a trovarci.",
        "Pesce freschissimo, vini di qualità, carne selezionata dai migliori macellai della zona e pasta fatta in casa contraddistinguono il nostro locale.",
        "Ambiente rilassante e piacevole, piatti creati da mani esperte e specializzati in pietanze senza glutine."
      ],
      pillars: [
        { t: "Pesce freschissimo", d: "Selezionato ogni giorno" },
        { t: "Pasta fatta in casa", d: "Tirata a mano" },
        { t: "Carne selezionata", d: "Dai migliori macellai della zona" },
        { t: "Senza glutine", d: "Cucina dedicata per celiaci" }
      ]
    },
    piatti: {
      eyebrow: "I nostri piatti",
      title: "Le specialità della casa",
      hint: "Clicca un piatto per scomporlo",
      hintTouch: "Tocca un piatto per scomporlo",
      open: "Scopri gli ingredienti",
      openLabel: "Scomponi il piatto",
      ingNote: "Testo di esempio — da confermare",
      items: [
        { n: "Battuta di Fassona piemontese", d: "Manzo piemontese battuto al coltello", img: "../images/blog/blog2.jpg",
          ing: [
            { n: "Fassona piemontese", d: "Razza magra: proteine complete, ferro e vitamina B12", icon: "beef" },
            { n: "Sedano", d: "Fibre, potassio e vitamina K, poche calorie", icon: "celery" },
            { n: "Grana Padano", d: "Stagionato oltre 12 mesi: calcio e proteine, naturalmente privo di lattosio", icon: "cheese" },
            { n: "Olio extravergine", d: "Grassi monoinsaturi e vitamina E", icon: "oliveoil" }
          ]},
        { n: "Spaghetti alla bisque di crostacei", d: "Con briciole croccanti e pistacchio", img: "../images/blog/blog1.jpg",
          ing: [
            { n: "Crostacei", d: "Proteine magre, selenio e iodio", icon: "shellfish" },
            { n: "Pistacchio di Bronte", d: "Grassi insaturi, fibre e vitamina B6", icon: "pistachio" },
            { n: "Pomodoro", d: "Fonte di licopene e vitamina C", icon: "tomato" },
            { n: "Grano duro", d: "Carboidrati complessi a rilascio lento", icon: "wheat" }
          ]},
        { n: "Risotto all'Amarone", d: "Il classico veronese, mantecato lentamente", img: "../images/blog/blog3.jpg",
          ing: [
            { n: "Riso Vialone Nano", d: "Amido che manteca naturalmente; naturalmente senza glutine", icon: "rice" },
            { n: "Amarone della Valpolicella", d: "Vino veronese: polifenoli dell'uva; l'alcol evapora in cottura", icon: "wine" },
            { n: "Burro e Grana", d: "Calcio e vitamina A", icon: "butter" },
            { n: "Brodo di verdure", d: "Minerali e sapore senza grassi aggiunti", icon: "stock" }
          ]},
        { n: "Tagliata di tonno", d: "In crosta di sesamo, cipolla rossa in agrodolce", img: "../images/blog/blog5.jpg",
          ing: [
            { n: "Tonno rosso", d: "Omega-3 EPA e DHA, proteine magre, vitamina D", icon: "tuna" },
            { n: "Sesamo", d: "Calcio, ferro e grassi insaturi", icon: "sesame" },
            { n: "Cipolla rossa di Tropea", d: "Antociani e quercetina", icon: "onion" },
            { n: "Aceto balsamico", d: "Dolcezza senza zuccheri aggiunti", icon: "vinegar" }
          ]},
        { n: "Tagliatelle allo scoglio", d: "Cozze, vongole, gamberi e calamaretti", img: "../images/blog/blog4.jpg",
          ing: [
            { n: "Cozze e vongole", d: "Ferro, zinco e vitamina B12", icon: "mussels" },
            { n: "Gamberi", d: "Proteine magre e selenio", icon: "prawn" },
            { n: "Calamaretti", d: "Poche calorie, ricchi di fosforo", icon: "squid" },
            { n: "Prezzemolo e aglio", d: "Vitamina C e composti solforati", icon: "herbs" }
          ]},
        { n: "Semifreddo al pistacchio", d: "Cuore di amarena", img: "../images/blog/blog6.jpg",
          ing: [
            { n: "Pistacchio", d: "Grassi buoni, fibre e magnesio", icon: "pistachio" },
            { n: "Amarena", d: "Antociani, colore naturale", icon: "cherry" },
            { n: "Uova", d: "Proteine complete e colina", icon: "egg" },
            { n: "Panna fresca", d: "Calcio e vitamina A", icon: "cream" }
          ]}
      ]
    },
    menu: {
      eyebrow: "Il menù",
      title: "Il nostro menù",
      note: "Menù di esempio — in attesa dei piatti e dei prezzi definitivi.",
      gf: "Senza glutine",
      filters: { all: "Tutti", gf: "Senza glutine", fish: "Pesce", meat: "Carne", veg: "Vegetariano" },
      filterLabel: "Filtra il menù",
      empty: "Nessun piatto in questa categoria.",
      sections: [
        { name: "Antipasti", items: [
          { n: "Battuta di Fassona piemontese", d: "Battuta al coltello, sedano, scaglie di grana", p: "18", gf: true, diet: "meat" },
          { n: "Cappuccino di polipo", d: "Crema di patate, polipo, spuma tiepida", p: "16", gf: true, diet: "fish" },
          { n: "Tartare di tonno rosso", d: "Agrumi, avocado, olio all'erba cipollina", p: "19", diet: "fish" },
          { n: "Sarde in saor alla veronese", d: "Cipolla, uvetta, pinoli", p: "14", diet: "fish" }
        ]},
        { name: "Primi", items: [
          { n: "Spaghetti alla bisque di crostacei", d: "Briciole croccanti, pistacchio di Bronte", p: "22", diet: "fish" },
          { n: "Risotto all'Amarone della Valpolicella", d: "Mantecato al Monte Veronese", p: "20", gf: true, diet: "veg" },
          { n: "Tagliolini ai porcini e tartufo", d: "Pasta fatta in casa, pepe nero", p: "24", diet: "veg" },
          { n: "Tagliatelle allo scoglio", d: "Cozze, vongole, gamberi, calamaretti", p: "23", diet: "fish" },
          { n: "Bigoli con le sarde", d: "Ricetta tradizionale veneta", p: "17", diet: "fish" }
        ]},
        { name: "Secondi", items: [
          { n: "Tagliata di tonno in crosta di sesamo", d: "Cipolla rossa in agrodolce", p: "26", diet: "fish" },
          { n: "Bollito misto di carne con pearà", d: "La tradizione veronese, servita al carrello", p: "24", diet: "meat" },
          { n: "Costata di manzo", d: "Frollatura 40 giorni, sale di Maldon", p: "28", gf: true, diet: "meat" },
          { n: "Branzino in crosta di patate", d: "Verdure di stagione", p: "25", gf: true, diet: "fish" }
        ]},
        { name: "Dolci", items: [
          { n: "Semifreddo al pistacchio", d: "Cuore di amarena", p: "9", diet: "veg" },
          { n: "Tiramisù della casa", d: "Savoiardi fatti in casa", p: "8", diet: "veg" },
          { n: "Sorbetto all'Amarone", d: "", p: "7", gf: true, diet: "veg" }
        ]}
      ]
    },
    galleria: { eyebrow: "Galleria", title: "Il locale", sub: "Una sala piccola e accogliente, nel vicolo dietro la piazza." },
    recensioni: {
      eyebrow: "Recensioni", title: "Cosa dicono di noi",
      items: [
        { t: "Fantastica!", q: "Osteria da provare assolutamente: ambiente molto confortevole con buona musica di sottofondo, non grande ma molto accogliente, personale preparato, attento e cordiale. Ottimi i piatti sia di carne che di pesce, e dolci sublimi." },
        { t: "Una rivelazione", q: "Qualità del cibo eccellente — il cappuccino di polipo è stato una rivelazione sia nel gusto che nella presentazione. Personale molto attento e gentile, esperto nel consigliare un buon vino. Lo consiglio, ma prenotate." },
        { t: "Consiglio azzeccato", q: "Piccola osteria in Vicolo Cadrega, zona frequentata da veronesi e poco dai turisti. Personale gentile. Piatti molto buoni e, considerata la qualità proposta, i prezzi si possono ritenere onesti." },
        { t: "Scelta eccellente", q: "Costata di manzo e tagliata di tonno TOP! Personale molto cordiale, cibo squisito e locale piccolo ma davvero grazioso. Nel complesso una scelta eccellente per una cena a Verona." }
      ]
    },
    prenota: {
      eyebrow: "Prenotazioni", title: "Prenota un tavolo",
      intro: "Chiamaci o scrivici — rispondiamo sempre. Per gruppi numerosi consigliamo di prenotare con qualche giorno di anticipo.",
      f: { date: "Data", time: "Orario", people: "Persone", name: "Nome e cognome",
           phone: "Telefono", email: "Email", notes: "Note (allergie, celiachia, occasioni speciali)",
           submit: "Invia richiesta", or: "oppure" },
      call: "Chiama 045 8015604",
      giftTitle: "Buoni regalo",
      giftBody: "Disponibili da 50, 100, 150 e 200 euro. Scriveteci per acquistarli."
    },
    contatti: {
      eyebrow: "Contatti", title: "Dove siamo",
      addrLabel: "Indirizzo", hoursLabel: "Orario", contactLabel: "Contatti",
      hours: "Da lunedì a domenica<br>orario continuato 12.00 – 22.00",
      addr: "Vicolo Cadrega 2/a<br>37121 Verona"
    },
    footer: { rights: "Tutti i diritti riservati", privacy: "Privacy Policy", cookie: "Cookie Policy" },
    a11y: { close: "Chiudi", skip: "Vai al contenuto" }
  },

  en: {
    langLabel: "EN",
    nav: { home: "Home", storia: "Our story", menu: "Menu", galleria: "Gallery", contatti: "Contact" },
    hero: {
      eyebrow: "Verona · since 1988",
      title: "Osteria<br>il Bertoldo",
      sub: "Quality dining in the heart of Verona's old town",
      ctaBook: "Book a table",
      ctaMenu: "See the menu",
      scroll: "Scroll"
    },
    storia: {
      eyebrow: "Our story",
      title: "In the heart of Verona since 1988",
      body: [
        "If you are looking for a dining experience out of the ordinary, built on dishes of the highest quality, come and find us.",
        "The freshest fish, fine wines, meat selected from the best butchers in the region and pasta made in our own kitchen are what define this place.",
        "A relaxed and welcoming room, dishes made by experienced hands, and a kitchen that specialises in gluten-free cooking."
      ],
      pillars: [
        { t: "The freshest fish", d: "Selected every morning" },
        { t: "House-made pasta", d: "Rolled by hand" },
        { t: "Selected meat", d: "From the region's best butchers" },
        { t: "Gluten free", d: "A dedicated coeliac kitchen" }
      ]
    },
    piatti: {
      eyebrow: "Our dishes",
      title: "House specialities",
      hint: "Click a dish to break it apart",
      hintTouch: "Tap a dish to break it apart",
      open: "See the ingredients",
      openLabel: "Break the dish apart",
      ingNote: "Sample text — to be confirmed",
      items: [
        { n: "Piedmontese Fassona beef tartare", d: "Hand-cut with a knife", img: "../images/blog/blog2.jpg",
          ing: [
            { n: "Fassona beef", d: "A lean breed: complete protein, iron and vitamin B12", icon: "beef" },
            { n: "Celery", d: "Fibre, potassium and vitamin K, very low in calories", icon: "celery" },
            { n: "Grana Padano", d: "Aged over 12 months: calcium and protein, naturally lactose-free", icon: "cheese" },
            { n: "Extra virgin olive oil", d: "Monounsaturated fats and vitamin E", icon: "oliveoil" }
          ]},
        { n: "Spaghetti in shellfish bisque", d: "Crisp crumb and pistachio", img: "../images/blog/blog1.jpg",
          ing: [
            { n: "Shellfish", d: "Lean protein, selenium and iodine", icon: "shellfish" },
            { n: "Bronte pistachio", d: "Unsaturated fats, fibre and vitamin B6", icon: "pistachio" },
            { n: "Tomato", d: "A source of lycopene and vitamin C", icon: "tomato" },
            { n: "Durum wheat", d: "Slow-release complex carbohydrates", icon: "wheat" }
          ]},
        { n: "Amarone risotto", d: "The Veronese classic, stirred slowly", img: "../images/blog/blog3.jpg",
          ing: [
            { n: "Vialone Nano rice", d: "Starch that thickens on its own; naturally gluten-free", icon: "rice" },
            { n: "Amarone della Valpolicella", d: "The Veronese wine: grape polyphenols; the alcohol cooks off", icon: "wine" },
            { n: "Butter and Grana", d: "Calcium and vitamin A", icon: "butter" },
            { n: "Vegetable stock", d: "Minerals and flavour without added fat", icon: "stock" }
          ]},
        { n: "Seared tuna tagliata", d: "Sesame crust, sweet-and-sour red onion", img: "../images/blog/blog5.jpg",
          ing: [
            { n: "Bluefin tuna", d: "Omega-3 EPA and DHA, lean protein, vitamin D", icon: "tuna" },
            { n: "Sesame", d: "Calcium, iron and unsaturated fats", icon: "sesame" },
            { n: "Tropea red onion", d: "Anthocyanins and quercetin", icon: "onion" },
            { n: "Balsamic vinegar", d: "Sweetness with no added sugar", icon: "vinegar" }
          ]},
        { n: "Seafood tagliatelle", d: "Mussels, clams, prawns and baby squid", img: "../images/blog/blog4.jpg",
          ing: [
            { n: "Mussels and clams", d: "Iron, zinc and vitamin B12", icon: "mussels" },
            { n: "Prawns", d: "Lean protein and selenium", icon: "prawn" },
            { n: "Baby squid", d: "Low in calories, rich in phosphorus", icon: "squid" },
            { n: "Parsley and garlic", d: "Vitamin C and sulphur compounds", icon: "herbs" }
          ]},
        { n: "Pistachio semifreddo", d: "Sour cherry centre", img: "../images/blog/blog6.jpg",
          ing: [
            { n: "Pistachio", d: "Healthy fats, fibre and magnesium", icon: "pistachio" },
            { n: "Sour cherry", d: "Anthocyanins, natural colour", icon: "cherry" },
            { n: "Eggs", d: "Complete protein and choline", icon: "egg" },
            { n: "Fresh cream", d: "Calcium and vitamin A", icon: "cream" }
          ]}
      ]
    },
    menu: {
      eyebrow: "The menu",
      title: "Our menu",
      note: "Sample menu — awaiting the final dishes and prices.",
      gf: "Gluten free",
      filters: { all: "All", gf: "Gluten free", fish: "Fish", meat: "Meat", veg: "Vegetarian" },
      filterLabel: "Filter the menu",
      empty: "No dishes in this category.",
      sections: [
        { name: "Starters", items: [
          { n: "Piedmontese Fassona beef tartare", d: "Hand-cut, celery, aged grana", p: "18", gf: true, diet: "meat" },
          { n: "Octopus 'cappuccino'", d: "Potato cream, octopus, warm foam", p: "16", gf: true, diet: "fish" },
          { n: "Bluefin tuna tartare", d: "Citrus, avocado, chive oil", p: "19", diet: "fish" },
          { n: "Veronese sarde in saor", d: "Onion, raisins, pine nuts", p: "14", diet: "fish" }
        ]},
        { name: "First courses", items: [
          { n: "Spaghetti in shellfish bisque", d: "Crisp crumb, Bronte pistachio", p: "22", diet: "fish" },
          { n: "Amarone della Valpolicella risotto", d: "Finished with Monte Veronese", p: "20", gf: true, diet: "veg" },
          { n: "Tagliolini with porcini and truffle", d: "House-made pasta, black pepper", p: "24", diet: "veg" },
          { n: "Seafood tagliatelle", d: "Mussels, clams, prawns, baby squid", p: "23", diet: "fish" },
          { n: "Bigoli with sardines", d: "The traditional Veneto recipe", p: "17", diet: "fish" }
        ]},
        { name: "Main courses", items: [
          { n: "Sesame-crusted tuna tagliata", d: "Sweet-and-sour red onion", p: "26", diet: "fish" },
          { n: "Mixed boiled meats with pearà", d: "The Verona tradition, served from the trolley", p: "24", diet: "meat" },
          { n: "Beef rib steak", d: "40-day aged, Maldon salt", p: "28", gf: true, diet: "meat" },
          { n: "Potato-crusted sea bass", d: "Seasonal vegetables", p: "25", gf: true, diet: "fish" }
        ]},
        { name: "Desserts", items: [
          { n: "Pistachio semifreddo", d: "Sour cherry centre", p: "9", diet: "veg" },
          { n: "House tiramisù", d: "Home-made savoiardi", p: "8", diet: "veg" },
          { n: "Amarone sorbet", d: "", p: "7", gf: true, diet: "veg" }
        ]}
      ]
    },
    galleria: { eyebrow: "Gallery", title: "The room", sub: "A small, warm dining room in the lane behind the square." },
    recensioni: {
      eyebrow: "Reviews", title: "What our guests say",
      items: [
        { t: "Fantastic!", q: "An osteria absolutely worth trying: a very comfortable room with good music, not large but very welcoming, well-trained staff, attentive and warm. Excellent dishes both meat and fish, and sublime desserts." },
        { t: "A revelation", q: "Excellent food quality — the octopus cappuccino was a revelation both in flavour and presentation. Very attentive and kind staff, expert at recommending a good wine. I recommend it, but book ahead." },
        { t: "Spot-on recommendation", q: "A small osteria in Vicolo Cadrega, an area frequented by locals and rarely by tourists. Kind staff. Very good dishes, and considering the quality on offer the prices can be considered fair." },
        { t: "An excellent choice", q: "The rib steak and tuna tagliata were TOP! Very friendly staff, delicious food, a small but genuinely lovely room. All in all an excellent choice for dinner in Verona." }
      ]
    },
    prenota: {
      eyebrow: "Reservations", title: "Book a table",
      intro: "Call or write to us — we always reply. For larger groups we recommend booking a few days ahead.",
      f: { date: "Date", time: "Time", people: "Guests", name: "Full name", phone: "Phone", email: "Email", notes: "Notes (allergies, coeliac, special occasions)", submit: "Send request", or: "or" },
      call: "Call 045 8015604",
      giftTitle: "Gift vouchers",
      giftBody: "Available at 50, 100, 150 and 200 euro. Write to us to purchase."
    },
    contatti: {
      eyebrow: "Contact", title: "Find us",
      addrLabel: "Address", hoursLabel: "Opening hours", contactLabel: "Contact",
      hours: "Monday to Sunday<br>continuous service 12.00 – 22.00",
      addr: "Vicolo Cadrega 2/a<br>37121 Verona"
    },
    footer: { rights: "All rights reserved", privacy: "Privacy Policy", cookie: "Cookie Policy" },
    a11y: { close: "Close", skip: "Skip to content" }
  }
};

/* Dated notice — self-expiring. Set `until` and it disappears on its own.
   This replaces the old hard-coded "Chiusi 24-29 Gennaio 2026" popup
   that kept firing long after the date had passed. */
const NOTICE = {
  active: false,                 // flip to true when there is something to announce
  until: "2026-01-30",           // notice hides itself after this date
  it: { title: "Chiusi per ferie", body: "Dal 24 al 29 gennaio 2026. Per info scriveteci." },
  en: { title: "Closed for holidays", body: "24–29 January 2026. Write to us for information." }
};
