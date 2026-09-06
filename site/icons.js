/* ===========================================================
   Ingredient illustrations — hand-drawn inline SVG.

   Drawn rather than photographed on purpose: line art in the
   site's brass palette matches the engraved/vintage grade,
   carries no licensing risk, costs no extra requests, and
   stays sharp at any size. Every path is stroked with
   currentColor so the CSS controls the colour.
   =========================================================== */

const ICONS = {

  beef: `<path d="M14 26c-4-6-2-14 6-17 6-2 13 0 16 5 3 5 2 12-3 15-6 4-15 3-19-3z"/>
         <path d="M22 16c2-2 6-2 8 1M20 24c3 1 7 0 9-3" opacity=".55"/>
         <circle cx="27" cy="21" r="2.4" opacity=".5"/>`,

  celery: `<path d="M18 44c0-12 1-22 3-30M25 44c0-13 0-24-1-31M32 44c0-12-1-22-3-29"/>
           <path d="M14 16c2-6 6-9 8-9M36 16c-2-6-6-9-8-9" opacity=".6"/>
           <path d="M15 44h20" opacity=".45"/>`,

  cheese: `<path d="M6 32V20l19-8 19 8v12z"/>
           <path d="M6 20l19 8 19-8M25 28v12" opacity=".55"/>
           <circle cx="14" cy="25" r="1.8" opacity=".5"/>
           <circle cx="34" cy="26" r="2.2" opacity=".5"/>`,

  oliveoil: `<path d="M20 8h10v5l5 7v20a4 4 0 0 1-4 4H19a4 4 0 0 1-4-4V20l5-7z"/>
             <path d="M15 27h20" opacity=".5"/>
             <ellipse cx="25" cy="34" rx="5" ry="4" opacity=".55"/>`,

  shellfish: `<path d="M25 40c-9 0-16-6-16-13 0-4 3-7 7-7 3 0 5 2 6 4 1-3 2-6 3-8 1 2 2 5 3 8 1-2 3-4 6-4 4 0 7 3 7 7 0 7-7 13-16 13z"/>
              <path d="M25 16v24M17 22l4 16M33 22l-4 16" opacity=".5"/>`,

  pistachio: `<path d="M16 14c6-5 14-5 19 1 4 6 3 15-3 20-6 4-15 3-19-3-4-6-3-14 3-18z"/>
              <path d="M20 18c4-3 9-2 12 2" opacity=".55"/>
              <path d="M14 30c5 4 13 4 18-1" opacity=".45"/>`,

  tomato: `<circle cx="25" cy="28" r="14"/>
           <path d="M25 14c-2-4-5-5-8-5 2 3 3 5 3 6M25 14c2-4 5-5 8-5-2 3-3 5-3 6" opacity=".6"/>
           <path d="M18 24c1-3 4-5 7-5" opacity=".45"/>`,

  wheat: `<path d="M25 44V16"/>
          <path d="M25 18c-5-1-8-4-8-8 4 0 7 2 8 5M25 18c5-1 8-4 8-8-4 0-7 2-8 5"/>
          <path d="M25 27c-5-1-8-4-8-8 4 0 7 2 8 5M25 27c5-1 8-4 8-8-4 0-7 2-8 5" opacity=".7"/>
          <path d="M25 36c-5-1-8-4-8-8 4 0 7 2 8 5M25 36c5-1 8-4 8-8-4 0-7 2-8 5" opacity=".5"/>`,

  rice: `<ellipse cx="16" cy="20" rx="4" ry="7" transform="rotate(-20 16 20)"/>
         <ellipse cx="30" cy="17" rx="4" ry="7" transform="rotate(15 30 17)"/>
         <ellipse cx="22" cy="32" rx="4" ry="7" transform="rotate(-8 22 32)"/>
         <ellipse cx="34" cy="31" rx="4" ry="7" transform="rotate(28 34 31)" opacity=".65"/>`,

  wine: `<path d="M16 8h18l-2 12a7 7 0 0 1-14 0z"/>
         <path d="M25 27v12M18 40h14"/>
         <path d="M17 15h16" opacity=".5"/>`,

  butter: `<path d="M10 30l8-10h22l-8 10z"/>
           <path d="M10 30v8l22 0v-8M32 30l8-10v8l-8 10" opacity=".6"/>`,

  stock: `<path d="M11 20h28l-3 20a4 4 0 0 1-4 3H18a4 4 0 0 1-4-3z"/>
          <path d="M8 20h34" />
          <path d="M20 14c0-3 2-4 2-6M28 14c0-3 2-4 2-6" opacity=".55"/>`,

  tuna: `<path d="M6 26c6-8 16-12 24-10 5 1 10 4 14 10-4 6-9 9-14 10-8 2-18-2-24-10z"/>
         <path d="M6 26l-2-7 8 4M6 26l-2 7 8-4" opacity=".6"/>
         <circle cx="34" cy="24" r="1.8"/>
         <path d="M24 18c2 5 2 11 0 16" opacity=".45"/>`,

  sesame: `<ellipse cx="18" cy="22" rx="3.4" ry="5.4" transform="rotate(-25 18 22)"/>
           <ellipse cx="31" cy="19" rx="3.4" ry="5.4" transform="rotate(20 31 19)"/>
           <ellipse cx="24" cy="31" rx="3.4" ry="5.4" transform="rotate(-5 24 31)"/>
           <ellipse cx="34" cy="32" rx="3.4" ry="5.4" transform="rotate(35 34 32)" opacity=".6"/>`,

  onion: `<path d="M25 12c8 0 14 7 14 15s-6 15-14 15-14-7-14-15 6-15 14-15z"/>
          <path d="M25 12c-4 6-4 24 0 30M25 12c4 6 4 24 0 30" opacity=".5"/>
          <path d="M22 10c1-3 2-4 3-6 1 2 2 3 3 6" opacity=".6"/>`,

  vinegar: `<path d="M21 8h8v6l4 6v20a3 3 0 0 1-3 3H20a3 3 0 0 1-3-3V20l4-6z"/>
            <path d="M17 28h16" opacity=".5"/>
            <path d="M20 33h10" opacity=".35"/>`,

  mussels: `<path d="M8 30c2-8 10-14 18-14 6 0 10 3 12 8-3 8-11 13-19 13-6 0-10-3-11-7z"/>
            <path d="M12 28c4-5 11-8 17-8" opacity=".5"/>
            <path d="M20 18c-2 6-2 13 1 19" opacity=".45"/>`,

  prawn: `<path d="M38 14c-8-1-16 3-20 10-3 6-1 13 5 16 5 2 11 0 13-5"/>
          <path d="M38 14c3 3 4 7 3 10M22 24c3-2 7-2 10 0" opacity=".55"/>
          <circle cx="34" cy="18" r="1.6"/>
          <path d="M18 36c-3 2-6 2-9 1" opacity=".5"/>`,

  squid: `<path d="M25 8c7 0 12 5 12 12 0 4-2 7-4 9H17c-2-2-4-5-4-9C13 13 18 8 25 8z"/>
          <path d="M18 29c-1 6-2 10-4 13M23 29c-1 7-1 11-1 14M27 29c1 7 1 11 1 14M32 29c1 6 2 10 4 13" opacity=".6"/>
          <circle cx="21" cy="18" r="1.5"/><circle cx="29" cy="18" r="1.5"/>`,

  herbs: `<path d="M25 44c0-12 4-22 12-28"/>
          <path d="M31 22c-4-2-5-6-3-10 4 2 5 6 3 10zM26 30c-5-1-7-5-6-9 4 1 7 5 6 9z" opacity=".75"/>
          <path d="M25 44c0-9-3-16-9-21"/>
          <path d="M18 26c3-2 4-5 3-9-3 2-4 6-3 9z" opacity=".6"/>`,

  cherry: `<circle cx="18" cy="33" r="7"/><circle cx="32" cy="35" r="6.5"/>
           <path d="M18 26c1-8 5-13 11-16M32 28c-1-7 0-12 4-15" opacity=".6"/>
           <path d="M16 31c1-2 2-3 4-3" opacity=".45"/>`,

  egg: `<ellipse cx="25" cy="27" rx="12" ry="15"/>
        <path d="M18 22c1-4 4-6 7-6" opacity=".5"/>`,

  cream: `<path d="M14 18h22l-2 22a4 4 0 0 1-4 4H20a4 4 0 0 1-4-4z"/>
          <path d="M14 18c0-4 5-7 11-7s11 3 11 7" />
          <path d="M18 26c3 2 7 2 10 0" opacity=".5"/>`,

  garlic: `<path d="M25 10c6 6 10 13 10 20 0 7-4 12-10 12s-10-5-10-12c0-7 4-14 10-20z"/>
           <path d="M25 12v30M19 22c2 6 2 14 0 19M31 22c-2 6-2 14 0 19" opacity=".5"/>`
};

/* which drawing each ingredient uses — keyed off the icon name stored
   in content.js, so IT and EN share one illustration */
function iconSvg(name){
  const d = ICONS[name] || ICONS.herbs;
  return `<svg class="ing-ico" width="32" height="32" viewBox="0 0 50 50" aria-hidden="true" focusable="false">${d}</svg>`;
}
