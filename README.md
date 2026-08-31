# DeLokaleGidsMedia

Astro 5 statische site voor **delokalegidsmedia.nl**, overgezet vanaf
WordPress.

Uitgerold op Cloudflare Workers in het account **info@zbseo.uk**
(`54b144d6...`, subdomein `muddy-heart-fc18`):

- https://delokalegidsmedia.muddy-heart-fc18.workers.dev

Het productiedomein hangt er nog niet aan. Zodra de nameservers naar
Cloudflare zijn doorgezet:

```toml
routes = [
  { pattern = "delokalegidsmedia.nl", custom_domain = true },
  { pattern = "www.delokalegidsmedia.nl", custom_domain = true },
]
```

## Commando's

```bash
npm install
npm run dev
npm run build
npm run deploy    # build + wrangler deploy
```

## Wat voor site dit is

Een eenpagina-site: de uitgeverij achter een reeks lokale gidswebsites. De
pagina bestaat uit een hero, vier korte beloftes met elk een eigen icoon, de
lijst met **98 regionale uitgaves**, een blok over de portals en een
contactsectie.

| Pad | Inhoud |
| --- | --- |
| `/` | de hele site |
| `/sitemap-index.xml` | XML-sitemap |
| `/404/` | foutpagina |

## Waar de inhoud vandaan komt

De REST API, de sitemap, de feed en zelfs `robots.txt` van de oude site geven
allemaal een **500**; alleen de voorpagina doet het. Het Internet Archive kent
ook geen andere pagina's van dit domein — alleen de voorpagina en een los
`webmail`-subdomein. Er is dus geen aanwijzing dat er meer pagina's zijn.

De inhoud komt daarom uit een HTML-spiegel van de voorpagina.
`migration/scripts_build_content.py` leest die gestructureerd uit — de
SEO-meta, de kop en intro, de vier beloftes met hun iconen, de sectieteksten
en de 98 gidsen — in plaats van de Elementor-markup plat te slaan. Dat laatste
levert losse zinnen zonder verband op; zie de voorpagina van schoonmakerweb
voor hoe dat misgaat.

`migration/scripts_download_images.py` haalt de 13 afbeeldingen op naar
`public/wp-content/uploads/`, op hetzelfde pad als op de oude site.

## Nog in te vullen

Het contactformulier liep op de oude site via Elementor Forms. Zet een
Web3Forms access key in `contact.web3formsKey` in `src/data/site.ts` en het
formulier verstuurt weer echt; zolang die leeg is toont de contactsectie een
korte melding in plaats van een formulier dat stilletjes niets doet. Op de
oude pagina staat geen zichtbaar mailadres, dus er is ook geen adres om als
terugvaloptie te tonen.

## Ontwerp

Kleuren en typografie komen uit de Elementor-kit van de oude site: Montserrat,
zwart als basis, rood en amber `#FFB700` als accenten. Het rood is iets
ingetogener gezet (`#e01b1b` in plaats van `#ff0000`) zodat het als accent
werkt en niet als vlak.
