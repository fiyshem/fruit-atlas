#!/usr/bin/env python3
"""Build the Fruit Atlas catalogue from the included species and cultivar seed files.

The generated index intentionally distinguishes botanical species, named cultivars,
and editorial fruit-form guides. Form guides describe patterns to look for; they are
not presented as individually verified cultivar names.
"""
import json, re, unicodedata, hashlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'

# name | scientific name | family | group | broad origin
ROWS = r'''
Apple|Malus domestica|Rosaceae|Pomes & temperate fruits|Central Asia
Asian pear|Pyrus pyrifolia|Rosaceae|Pomes & temperate fruits|East Asia
European pear|Pyrus communis|Rosaceae|Pomes & temperate fruits|Europe and western Asia
Quince|Cydonia oblonga|Rosaceae|Pomes & temperate fruits|Caucasus and western Asia
Medlar|Mespilus germanica|Rosaceae|Pomes & temperate fruits|Southwest Asia and southeastern Europe
Loquat|Eriobotrya japonica|Rosaceae|Pomes & temperate fruits|China
Japanese pear|Pyrus pyrifolia|Rosaceae|Pomes & temperate fruits|East Asia
Nashi pear|Pyrus pyrifolia|Rosaceae|Pomes & temperate fruits|East Asia
Serviceberry|Amelanchier alnifolia|Rosaceae|Wild & woodland fruits|North America
Juneberry|Amelanchier canadensis|Rosaceae|Wild & woodland fruits|North America
Rowan berry|Sorbus aucuparia|Rosaceae|Wild & woodland fruits|Europe and northern Asia
Hawthorn berry|Crataegus monogyna|Rosaceae|Wild & woodland fruits|Europe, northwest Africa and western Asia
Rose hip|Rosa canina|Rosaceae|Wild & woodland fruits|Europe and western Asia
Apricot|Prunus armeniaca|Rosaceae|Stone fruits|Central and eastern Asia
Peach|Prunus persica|Rosaceae|Stone fruits|China
Nectarine|Prunus persica var. nucipersica|Rosaceae|Stone fruits|China
Flat peach|Prunus persica var. platycarpa|Rosaceae|Stone fruits|China
Plum|Prunus domestica|Rosaceae|Stone fruits|Europe and western Asia
Japanese plum|Prunus salicina|Rosaceae|Stone fruits|China
Damson|Prunus domestica subsp. insititia|Rosaceae|Stone fruits|Europe and western Asia
Greengage|Prunus domestica subsp. italica|Rosaceae|Stone fruits|Europe and western Asia
Mirabelle plum|Prunus domestica subsp. syriaca|Rosaceae|Stone fruits|Western Asia and Europe
Cherry plum|Prunus cerasifera|Rosaceae|Stone fruits|Southeastern Europe and western Asia
Sweet cherry|Prunus avium|Rosaceae|Stone fruits|Europe and western Asia
Sour cherry|Prunus cerasus|Rosaceae|Stone fruits|Europe and western Asia
Cornelian cherry|Cornus mas|Cornaceae|Wild & woodland fruits|Europe and western Asia
Blackthorn fruit|Prunus spinosa|Rosaceae|Wild & woodland fruits|Europe and western Asia
Strawberry|Fragaria × ananassa|Rosaceae|Berries & small fruits|Europe, from cultivated hybrid ancestry
Wild strawberry|Fragaria vesca|Rosaceae|Berries & small fruits|Northern hemisphere
Alpine strawberry|Fragaria vesca var. semperflorens|Rosaceae|Berries & small fruits|Europe and Asia
Raspberry|Rubus idaeus|Rosaceae|Berries & small fruits|Europe and northern Asia
Black raspberry|Rubus occidentalis|Rosaceae|Berries & small fruits|Eastern North America
Blackberry|Rubus fruticosus agg.|Rosaceae|Berries & small fruits|Europe and western Asia
Dewberry|Rubus caesius|Rosaceae|Berries & small fruits|Europe and Asia
Boysenberry|Rubus ursinus × Rubus idaeus|Rosaceae|Berries & small fruits|California, United States
Loganberry|Rubus × loganobaccus|Rosaceae|Berries & small fruits|California, United States
Marionberry|Rubus L. hybrid|Rosaceae|Berries & small fruits|Oregon, United States
Salmonberry|Rubus spectabilis|Rosaceae|Berries & small fruits|Pacific coast of North America
Wineberry|Rubus phoenicolasius|Rosaceae|Berries & small fruits|East Asia
Cloudberry|Rubus chamaemorus|Rosaceae|Berries & small fruits|Arctic and boreal regions
Thimbleberry|Rubus parviflorus|Rosaceae|Berries & small fruits|Western North America
Blueberry|Vaccinium corymbosum|Ericaceae|Berries & small fruits|Eastern North America
Lowbush blueberry|Vaccinium angustifolium|Ericaceae|Berries & small fruits|Eastern North America
Bilberry|Vaccinium myrtillus|Ericaceae|Berries & small fruits|Europe and northern Asia
Cranberry|Vaccinium macrocarpon|Ericaceae|Berries & small fruits|North America
Lingonberry|Vaccinium vitis-idaea|Ericaceae|Berries & small fruits|Northern hemisphere
Huckleberry|Vaccinium membranaceum|Ericaceae|Berries & small fruits|Western North America
Bearberry|Arctostaphylos uva-ursi|Ericaceae|Wild & woodland fruits|Northern hemisphere
Aronia|Aronia melanocarpa|Rosaceae|Berries & small fruits|Eastern North America
Chokecherry|Prunus virginiana|Rosaceae|Wild & woodland fruits|North America
Elderberry|Sambucus nigra|Adoxaceae|Berries & small fruits|Europe and western Asia
Blackcurrant|Ribes nigrum|Grossulariaceae|Berries & small fruits|Northern Europe and Asia
Redcurrant|Ribes rubrum|Grossulariaceae|Berries & small fruits|Europe and western Asia
White currant|Ribes rubrum|Grossulariaceae|Berries & small fruits|Europe and western Asia
Gooseberry|Ribes uva-crispa|Grossulariaceae|Berries & small fruits|Europe and western Asia
Cape gooseberry|Physalis peruviana|Solanaceae|Berries & small fruits|Andes
Goldenberry|Physalis peruviana|Solanaceae|Berries & small fruits|Andes
Ground cherry|Physalis pruinosa|Solanaceae|Berries & small fruits|Central and North America
Tomatillo|Physalis philadelphica|Solanaceae|Botanical fruits & unusual edibles|Mexico
Goji berry|Lycium barbarum|Solanaceae|Berries & small fruits|China
Sea buckthorn|Hippophae rhamnoides|Elaeagnaceae|Berries & small fruits|Europe and Asia
Maqui berry|Aristotelia chilensis|Elaeocarpaceae|Berries & small fruits|Southern Chile and Argentina
Açaí|Euterpe oleracea|Arecaceae|Palm & arid-region fruits|Amazon basin
Acai palm fruit|Euterpe oleracea|Arecaceae|Palm & arid-region fruits|Amazon basin
Mulberry|Morus alba|Moraceae|Berries & small fruits|China
Black mulberry|Morus nigra|Moraceae|Berries & small fruits|Western Asia
Red mulberry|Morus rubra|Moraceae|Berries & small fruits|Eastern North America
Grape|Vitis vinifera|Vitaceae|Grapes & vine fruits|Western Asia and the Mediterranean
Fox grape|Vitis labrusca|Vitaceae|Grapes & vine fruits|Eastern North America
Muscadine grape|Vitis rotundifolia|Vitaceae|Grapes & vine fruits|Southeastern United States
Sea grape|Coccoloba uvifera|Polygonaceae|Wild & woodland fruits|Caribbean and tropical Americas
Citrus orange|Citrus × sinensis|Rutaceae|Citrus fruits|Southeast Asia
Sweet orange|Citrus × sinensis|Rutaceae|Citrus fruits|Southeast Asia
Blood orange|Citrus × sinensis|Rutaceae|Citrus fruits|Mediterranean region
Mandarin|Citrus reticulata|Rutaceae|Citrus fruits|China
Tangerine|Citrus tangerina|Rutaceae|Citrus fruits|Southeast Asia
Satsuma|Citrus unshiu|Rutaceae|Citrus fruits|Japan
Clementine|Citrus × clementina|Rutaceae|Citrus fruits|Algeria, from cultivated ancestry
Grapefruit|Citrus × paradisi|Rutaceae|Citrus fruits|Caribbean, from citrus ancestry
Pomelo|Citrus maxima|Rutaceae|Citrus fruits|Southeast Asia
Lemon|Citrus × limon|Rutaceae|Citrus fruits|Northeastern India and nearby regions
Lime|Citrus × aurantiifolia|Rutaceae|Citrus fruits|South and Southeast Asia
Persian lime|Citrus × latifolia|Rutaceae|Citrus fruits|Cultivated hybrid; exact origin uncertain
Key lime|Citrus × aurantiifolia|Rutaceae|Citrus fruits|South and Southeast Asia
Makrut lime|Citrus hystrix|Rutaceae|Citrus fruits|Southeast Asia
Finger lime|Citrus australasica|Rutaceae|Citrus fruits|Eastern Australia
Yuzu|Citrus junos|Rutaceae|Citrus fruits|China and Tibet; cultivated in Japan
Bergamot orange|Citrus bergamia|Rutaceae|Citrus fruits|Southern Italy
Citron|Citrus medica|Rutaceae|Citrus fruits|Northeastern India
Buddha's hand|Citrus medica var. sarcodactylis|Rutaceae|Citrus fruits|East Asia
Kumquat|Citrus japonica|Rutaceae|Citrus fruits|East Asia
Calamansi|Citrus × microcarpa|Rutaceae|Citrus fruits|Philippines
Sweet lime|Citrus limetta|Rutaceae|Citrus fruits|South Asia and Southeast Asia
Sudachi|Citrus sudachi|Rutaceae|Citrus fruits|Japan
Kabosu|Citrus sphaerocarpa|Rutaceae|Citrus fruits|Japan
Tangelo|Citrus × tangelo|Rutaceae|Citrus fruits|Cultivated citrus hybrid
Ugli fruit|Citrus reticulata × Citrus maxima ancestry|Rutaceae|Citrus fruits|Jamaica
Kaffir lime|Citrus hystrix|Rutaceae|Citrus fruits|Southeast Asia
Meyer lemon|Citrus × meyeri|Rutaceae|Citrus fruits|China
Mango|Mangifera indica|Anacardiaceae|Tropical & subtropical fruits|South Asia
Banana|Musa acuminata × Musa balbisiana ancestry|Musaceae|Tropical & subtropical fruits|Southeast Asia
Plantain|Musa × paradisiaca|Musaceae|Tropical & subtropical fruits|Southeast Asia
Red banana|Musa acuminata group|Musaceae|Tropical & subtropical fruits|Southeast Asia
Blue Java banana|Musa acuminata × Musa balbisiana ancestry|Musaceae|Tropical & subtropical fruits|Southeast Asia
Pisang Awak banana|Musa ABB group|Musaceae|Tropical & subtropical fruits|Southeast Asia
Cooking banana|Musa spp.|Musaceae|Tropical & subtropical fruits|Southeast Asia
Pineapple|Ananas comosus|Bromeliaceae|Tropical & subtropical fruits|South America
Papaya|Carica papaya|Caricaceae|Tropical & subtropical fruits|Southern Mexico and Central America
Avocado|Persea americana|Lauraceae|Tropical & subtropical fruits|Mexico and Central America
Coconut|Cocos nucifera|Arecaceae|Palm & arid-region fruits|Indo-Pacific region
Date|Phoenix dactylifera|Arecaceae|Palm & arid-region fruits|Middle East and North Africa
Jujube|Ziziphus jujuba|Rhamnaceae|Pomes & temperate fruits|China
Indian jujube|Ziziphus mauritiana|Rhamnaceae|Tropical & subtropical fruits|South Asia
Ber|Ziziphus mauritiana|Rhamnaceae|Tropical & subtropical fruits|South Asia
Guava|Psidium guajava|Myrtaceae|Tropical & subtropical fruits|Tropical America
Strawberry guava|Psidium cattleyanum|Myrtaceae|Tropical & subtropical fruits|Eastern Brazil
Pineapple guava|Acca sellowiana|Myrtaceae|Tropical & subtropical fruits|Southern Brazil and northern Argentina
Feijoa|Acca sellowiana|Myrtaceae|Tropical & subtropical fruits|Southern Brazil and northern Argentina
Passion fruit|Passiflora edulis|Passifloraceae|Tropical & subtropical fruits|South America
Sweet granadilla|Passiflora ligularis|Passifloraceae|Tropical & subtropical fruits|Andes
Giant granadilla|Passiflora quadrangularis|Passifloraceae|Tropical & subtropical fruits|Tropical Americas
Banana passionfruit|Passiflora tripartita var. mollissima|Passifloraceae|Tropical & subtropical fruits|Andes
Dragon fruit|Selenicereus undatus|Cactaceae|Cacti & dryland fruits|Mexico and Central America
Red dragon fruit|Selenicereus costaricensis|Cactaceae|Cacti & dryland fruits|Central America
Yellow dragon fruit|Selenicereus megalanthus|Cactaceae|Cacti & dryland fruits|Northern South America
Prickly pear|Opuntia ficus-indica|Cactaceae|Cacti & dryland fruits|Mexico
Barbary fig|Opuntia ficus-indica|Cactaceae|Cacti & dryland fruits|Mexico
Saguaro fruit|Carnegiea gigantea|Cactaceae|Cacti & dryland fruits|Sonoran Desert
Pitaya|Selenicereus spp.|Cactaceae|Cacti & dryland fruits|Tropical Americas
Watermelon|Citrullus lanatus|Cucurbitaceae|Melons & gourds|Northeast Africa
Cantaloupe|Cucumis melo var. cantalupensis|Cucurbitaceae|Melons & gourds|Africa and western Asia; long cultivated
Honeydew melon|Cucumis melo inodorus group|Cucurbitaceae|Melons & gourds|Cultivated melon group
Canary melon|Cucumis melo inodorus group|Cucurbitaceae|Melons & gourds|Cultivated melon group
Piel de Sapo melon|Cucumis melo inodorus group|Cucurbitaceae|Melons & gourds|Spain
Galia melon|Cucumis melo reticulatus group|Cucurbitaceae|Melons & gourds|Israel, developed in cultivation
Persian melon|Cucumis melo|Cucurbitaceae|Melons & gourds|Cultivated melon group
Kiwano|Cucumis metulifer|Cucurbitaceae|Melons & gourds|Southern Africa
Horned melon|Cucumis metulifer|Cucurbitaceae|Melons & gourds|Southern Africa
Tamarind|Tamarindus indica|Fabaceae|Tropical & subtropical fruits|Tropical Africa
Jackfruit|Artocarpus heterophyllus|Moraceae|Tropical & subtropical fruits|South Asia
Breadfruit|Artocarpus altilis|Moraceae|Tropical & subtropical fruits|New Guinea and western Pacific
Breadnut|Brosimum alicastrum|Moraceae|Tropical & subtropical fruits|Central America and Caribbean
Cempedak|Artocarpus integer|Moraceae|Tropical & subtropical fruits|Southeast Asia
Marang|Artocarpus odoratissimus|Moraceae|Tropical & subtropical fruits|Borneo
Chempedak|Artocarpus integer|Moraceae|Tropical & subtropical fruits|Southeast Asia
Durian|Durio zibethinus|Malvaceae|Tropical & subtropical fruits|Southeast Asia
Mangosteen|Garcinia mangostana|Clusiaceae|Tropical & subtropical fruits|Sunda Islands and Malay Peninsula
Kokum|Garcinia indica|Clusiaceae|Tropical & subtropical fruits|Western India
Garcinia cambogia fruit|Garcinia gummi-gutta|Clusiaceae|Tropical & subtropical fruits|South and Southeast Asia
Rambutan|Nephelium lappaceum|Sapindaceae|Tropical & subtropical fruits|Southeast Asia
Pulasan|Nephelium ramboutan-ake|Sapindaceae|Tropical & subtropical fruits|Malay Peninsula
Lychee|Litchi chinensis|Sapindaceae|Tropical & subtropical fruits|Southern China
Longan|Dimocarpus longan|Sapindaceae|Tropical & subtropical fruits|South China and Southeast Asia
Mammea apple|Mammea americana|Calophyllaceae|Tropical & subtropical fruits|Caribbean
Sapodilla|Manilkara zapota|Sapotaceae|Tropical & subtropical fruits|Mexico and Central America
Chikoo|Manilkara zapota|Sapotaceae|Tropical & subtropical fruits|Mexico and Central America
Black sapote|Diospyros nigra|Ebenaceae|Tropical & subtropical fruits|Mexico and Central America
White sapote|Casimiroa edulis|Rutaceae|Tropical & subtropical fruits|Mexico and Central America
Mamey sapote|Pouteria sapota|Sapotaceae|Tropical & subtropical fruits|Central America
Canistel|Pouteria campechiana|Sapotaceae|Tropical & subtropical fruits|Central America
Lucuma|Pouteria lucuma|Sapotaceae|Tropical & subtropical fruits|Andes
Abiu|Pouteria caimito|Sapotaceae|Tropical & subtropical fruits|Amazon basin
Star apple|Chrysophyllum cainito|Sapotaceae|Tropical & subtropical fruits|Caribbean and Central America
African star apple|Chrysophyllum albidum|Sapotaceae|Tropical & subtropical fruits|Tropical Africa
African mango|Irvingia gabonensis|Irvingiaceae|Tropical & subtropical fruits|West and Central Africa
Marula|Sclerocarya birrea|Anacardiaceae|Tropical & subtropical fruits|Southern and eastern Africa
Safou|Dacryodes edulis|Burseraceae|Tropical & subtropical fruits|Central and western Africa
Baobab fruit|Adansonia digitata|Malvaceae|Tropical & subtropical fruits|Africa
Monkey orange|Strychnos spinosa|Loganiaceae|Tropical & subtropical fruits|Sub-Saharan Africa
Velvet tamarind|Dialium guineense|Fabaceae|Tropical & subtropical fruits|West Africa
Desert date|Balanites aegyptiaca|Zygophyllaceae|Palm & arid-region fruits|Africa and western Asia
Tendu fruit|Diospyros melanoxylon|Ebenaceae|Tropical & subtropical fruits|South Asia
Jamun|Syzygium cumini|Myrtaceae|Tropical & subtropical fruits|Indian subcontinent and Southeast Asia
Java plum|Syzygium cumini|Myrtaceae|Tropical & subtropical fruits|Indian subcontinent and Southeast Asia
Amla|Phyllanthus emblica|Phyllanthaceae|Tropical & subtropical fruits|South and Southeast Asia
Indian gooseberry|Phyllanthus emblica|Phyllanthaceae|Tropical & subtropical fruits|South and Southeast Asia
Bael|Aegle marmelos|Rutaceae|Tropical & subtropical fruits|Indian subcontinent
Wood apple|Limonia acidissima|Rutaceae|Tropical & subtropical fruits|South Asia
Elephant apple|Dillenia indica|Dilleniaceae|Tropical & subtropical fruits|South and Southeast Asia
Phalsa|Grewia asiatica|Malvaceae|Tropical & subtropical fruits|South Asia
Karonda|Carissa carandas|Apocynaceae|Tropical & subtropical fruits|South Asia
Kewra fruit|Pandanus odorifer|Pandanaceae|Tropical & subtropical fruits|South and Southeast Asia
Khejri pod|Prosopis cineraria|Fabaceae|Palm & arid-region fruits|South Asia
Mahua fruit|Madhuca longifolia|Sapotaceae|Tropical & subtropical fruits|South Asia
Kaffir plum|Harpephyllum caffrum|Anacardiaceae|Tropical & subtropical fruits|Southern Africa
Kakadu plum|Terminalia ferdinandiana|Combretaceae|Tropical & subtropical fruits|Northern Australia
Davidson's plum|Davidsonia jerseyana|Cunoniaceae|Tropical & subtropical fruits|Eastern Australia
Quandong|Santalum acuminatum|Santalaceae|Tropical & subtropical fruits|Australia
Muntries|Kunzea pomifera|Myrtaceae|Wild & woodland fruits|Southern Australia
Riberry|Syzygium luehmannii|Myrtaceae|Wild & woodland fruits|Eastern Australia
Lilly pilly|Syzygium smithii|Myrtaceae|Wild & woodland fruits|Eastern Australia
Finger lime|Citrus australasica|Rutaceae|Citrus fruits|Eastern Australia
Desert lime|Citrus glauca|Rutaceae|Citrus fruits|Australia
Illawarra plum|Podocarpus elatus|Podocarpaceae|Wild & woodland fruits|Eastern Australia
Burdekin plum|Pleiogynium timorense|Anacardiaceae|Tropical & subtropical fruits|Northern Australia and Pacific
Bunya nut|Araucaria bidwillii|Araucariaceae|Botanical fruits & unusual edibles|Queensland, Australia
Quandong peach|Santalum acuminatum|Santalaceae|Tropical & subtropical fruits|Australia
Arazá|Eugenia stipitata|Myrtaceae|Tropical & subtropical fruits|Amazon basin
Camu camu|Myrciaria dubia|Myrtaceae|Tropical & subtropical fruits|Western Amazon basin
Cupuacu|Theobroma grandiflorum|Malvaceae|Tropical & subtropical fruits|Amazon basin
Cacao fruit|Theobroma cacao|Malvaceae|Tropical & subtropical fruits|Tropical Americas
Cupuaçu|Theobroma grandiflorum|Malvaceae|Tropical & subtropical fruits|Amazon basin
Jabuticaba|Plinia cauliflora|Myrtaceae|Tropical & subtropical fruits|Brazil
Pitanga|Eugenia uniflora|Myrtaceae|Tropical & subtropical fruits|South America
Surinam cherry|Eugenia uniflora|Myrtaceae|Tropical & subtropical fruits|South America
Grumichama|Eugenia brasiliensis|Myrtaceae|Tropical & subtropical fruits|Brazil
Araza|Eugenia stipitata|Myrtaceae|Tropical & subtropical fruits|Amazon basin
Pequi|Caryocar brasiliense|Caryocaraceae|Tropical & subtropical fruits|Brazilian Cerrado
Bacuri|Platonia insignis|Clusiaceae|Tropical & subtropical fruits|Amazon basin
Uxi|Endopleura uchi|Humiriaceae|Tropical & subtropical fruits|Amazon basin
Patauá fruit|Oenocarpus bataua|Arecaceae|Palm & arid-region fruits|Amazon basin
Buriti fruit|Mauritia flexuosa|Arecaceae|Palm & arid-region fruits|Amazon basin
Miracle fruit|Synsepalum dulcificum|Sapotaceae|Tropical & subtropical fruits|West Africa
Ackee|Blighia sapida|Sapindaceae|Tropical & subtropical fruits|West Africa
Bilimbi|Averrhoa bilimbi|Oxalidaceae|Tropical & subtropical fruits|Southeast Asia
Starfruit|Averrhoa carambola|Oxalidaceae|Tropical & subtropical fruits|Southeast Asia
Carambola|Averrhoa carambola|Oxalidaceae|Tropical & subtropical fruits|Southeast Asia
Tamarillo|Solanum betaceum|Solanaceae|Tropical & subtropical fruits|Andes
Tree tomato|Solanum betaceum|Solanaceae|Tropical & subtropical fruits|Andes
Naranjilla|Solanum quitoense|Solanaceae|Tropical & subtropical fruits|Andes
Lulo|Solanum quitoense|Solanaceae|Tropical & subtropical fruits|Andes
Pepino melon|Solanum muricatum|Solanaceae|Tropical & subtropical fruits|Andes
Babaco|Vasconcellea × heilbornii|Caricaceae|Tropical & subtropical fruits|Andes
Chayote fruit|Sechium edule|Cucurbitaceae|Botanical fruits & unusual edibles|Mesoamerica
Tamarillo|Solanum betaceum|Solanaceae|Tropical & subtropical fruits|Andes
Cherimoya|Annona cherimola|Annonaceae|Tropical & subtropical fruits|Andes
Soursop|Annona muricata|Annonaceae|Tropical & subtropical fruits|Tropical Americas
Sugar apple|Annona squamosa|Annonaceae|Tropical & subtropical fruits|Tropical Americas
Custard apple|Annona squamosa|Annonaceae|Tropical & subtropical fruits|Tropical Americas
Atemoya|Annona × atemoya|Annonaceae|Tropical & subtropical fruits|Cultivated hybrid; tropical Americas
Rollinia|Annona mucosa|Annonaceae|Tropical & subtropical fruits|Amazon basin
Biriba|Annona mucosa|Annonaceae|Tropical & subtropical fruits|Amazon basin
Pawpaw|Asimina triloba|Annonaceae|Pomes & temperate fruits|Eastern North America
American pawpaw|Asimina triloba|Annonaceae|Pomes & temperate fruits|Eastern North America
Sweetsop|Annona squamosa|Annonaceae|Tropical & subtropical fruits|Tropical Americas
Santol|Sandoricum koetjape|Meliaceae|Tropical & subtropical fruits|Southeast Asia
Langsat|Lansium parasiticum|Meliaceae|Tropical & subtropical fruits|Southeast Asia
Lanzones|Lansium parasiticum|Meliaceae|Tropical & subtropical fruits|Southeast Asia
Duku|Lansium parasiticum|Meliaceae|Tropical & subtropical fruits|Southeast Asia
Burmese grape|Baccaurea ramiflora|Phyllanthaceae|Tropical & subtropical fruits|South and Southeast Asia
Rambai|Baccaurea motleyana|Phyllanthaceae|Tropical & subtropical fruits|Southeast Asia
Bignay|Antidesma bunius|Phyllanthaceae|Tropical & subtropical fruits|South and Southeast Asia
Ceylon gooseberry|Dovyalis hebecarpa|Salicaceae|Tropical & subtropical fruits|Sri Lanka
Acerola|Malpighia emarginata|Malpighiaceae|Tropical & subtropical fruits|Caribbean and Central America
Barbados cherry|Malpighia emarginata|Malpighiaceae|Tropical & subtropical fruits|Caribbean and Central America
Cashew apple|Anacardium occidentale|Anacardiaceae|Tropical & subtropical fruits|Northeastern Brazil
Rose apple|Syzygium jambos|Myrtaceae|Tropical & subtropical fruits|Southeast Asia
Malay apple|Syzygium malaccense|Myrtaceae|Tropical & subtropical fruits|Southeast Asia
Wax apple|Syzygium samarangense|Myrtaceae|Tropical & subtropical fruits|Southeast Asia
Water apple|Syzygium aqueum|Myrtaceae|Tropical & subtropical fruits|Southeast Asia
Java apple|Syzygium samarangense|Myrtaceae|Tropical & subtropical fruits|Southeast Asia
Otaheite apple|Syzygium malaccense|Myrtaceae|Tropical & subtropical fruits|Southeast Asia and Pacific
Keppel fruit|Stelechocarpus burahol|Annonaceae|Tropical & subtropical fruits|Java, Indonesia
Noni|Morinda citrifolia|Rubiaceae|Tropical & subtropical fruits|Southeast Asia and Australasia
Cheese fruit|Morinda citrifolia|Rubiaceae|Tropical & subtropical fruits|Southeast Asia and Australasia
Indian almond fruit|Terminalia catappa|Combretaceae|Tropical & subtropical fruits|Indo-Pacific
Burmese grape|Baccaurea ramiflora|Phyllanthaceae|Tropical & subtropical fruits|South and Southeast Asia
Pomegranate|Punica granatum|Lythraceae|Pomegranates & figs|Iran and surrounding regions
Fig|Ficus carica|Moraceae|Pomegranates & figs|Western Asia and Mediterranean
Smyrna fig|Ficus carica|Moraceae|Pomegranates & figs|Mediterranean region
Persimmon|Diospyros kaki|Ebenaceae|Pomegranates & figs|China
American persimmon|Diospyros virginiana|Ebenaceae|Pomegranates & figs|Eastern North America
Date-plum|Diospyros lotus|Ebenaceae|Pomegranates & figs|Southwest Asia
Olive|Olea europaea|Oleaceae|Botanical fruits & unusual edibles|Mediterranean basin
Black olive fruit|Olea europaea|Oleaceae|Botanical fruits & unusual edibles|Mediterranean basin
Green olive fruit|Olea europaea|Oleaceae|Botanical fruits & unusual edibles|Mediterranean basin
Tamarillo|Solanum betaceum|Solanaceae|Tropical & subtropical fruits|Andes
Prickly pear cactus fruit|Opuntia ficus-indica|Cactaceae|Cacti & dryland fruits|Mexico
Barrel cactus fruit|Ferocactus wislizeni|Cactaceae|Cacti & dryland fruits|Southwestern United States and Mexico
Saguaro berry|Carnegiea gigantea|Cactaceae|Cacti & dryland fruits|Sonoran Desert
Pitaya de mayo|Stenocereus griseus|Cactaceae|Cacti & dryland fruits|Mexico and Central America
Hylocereus fruit|Selenicereus undatus|Cactaceae|Cacti & dryland fruits|Central America
Tuna fruit|Opuntia spp.|Cactaceae|Cacti & dryland fruits|Americas
Kaffir lime berry|Citrus hystrix|Rutaceae|Citrus fruits|Southeast Asia
Palm date|Phoenix dactylifera|Arecaceae|Palm & arid-region fruits|Middle East and North Africa
Palmyra fruit|Borassus flabellifer|Arecaceae|Palm & arid-region fruits|South and Southeast Asia
Toddy palm fruit|Borassus flabellifer|Arecaceae|Palm & arid-region fruits|South and Southeast Asia
Sugar palm fruit|Arenga pinnata|Arecaceae|Palm & arid-region fruits|Southeast Asia
Nipa palm fruit|Nypa fruticans|Arecaceae|Palm & arid-region fruits|Indo-Pacific mangroves
Doum palm fruit|Hyphaene thebaica|Arecaceae|Palm & arid-region fruits|Northeast Africa
Peach palm fruit|Bactris gasipaes|Arecaceae|Palm & arid-region fruits|Central and South America
Cuban royal palm fruit|Roystonea regia|Arecaceae|Palm & arid-region fruits|Caribbean
Jelly palm fruit|Butia odorata|Arecaceae|Palm & arid-region fruits|South America
Macaw palm fruit|Acrocomia aculeata|Arecaceae|Palm & arid-region fruits|Central and South America
Pandanus fruit|Pandanus tectorius|Pandanaceae|Palm & arid-region fruits|Pacific and Indo-Pacific islands
Acerola cherry|Malpighia emarginata|Malpighiaceae|Tropical & subtropical fruits|Caribbean and Central America
Kiwifruit|Actinidia deliciosa|Actinidiaceae|Pomes & temperate fruits|China
Golden kiwifruit|Actinidia chinensis|Actinidiaceae|Pomes & temperate fruits|China
Hardy kiwi|Actinidia arguta|Actinidiaceae|Pomes & temperate fruits|East Asia
Arctic kiwi|Actinidia kolomikta|Actinidiaceae|Pomes & temperate fruits|East Asia
Jostaberry|Ribes × nidigrolaria|Grossulariaceae|Berries & small fruits|Cultivated European hybrid
Honeyberry|Lonicera caerulea|Caprifoliaceae|Berries & small fruits|Northern Asia and Europe
Haskap|Lonicera caerulea|Caprifoliaceae|Berries & small fruits|Northern Asia
Black chokeberry|Aronia melanocarpa|Rosaceae|Berries & small fruits|Eastern North America
Red chokeberry|Aronia arbutifolia|Rosaceae|Berries & small fruits|Eastern North America
Buffaloberry|Shepherdia argentea|Elaeagnaceae|Wild & woodland fruits|North America
Autumn olive fruit|Elaeagnus umbellata|Elaeagnaceae|Wild & woodland fruits|East Asia
Silverberry|Elaeagnus commutata|Elaeagnaceae|Wild & woodland fruits|North America
Hackberry|Celtis occidentalis|Cannabaceae|Wild & woodland fruits|North America
Sugarberry|Celtis laevigata|Cannabaceae|Wild & woodland fruits|Southern North America
Persian mulberry|Morus nigra|Moraceae|Berries & small fruits|Western Asia
Cloudberry|Rubus chamaemorus|Rosaceae|Berries & small fruits|Arctic and boreal regions
Crowberry|Empetrum nigrum|Ericaceae|Wild & woodland fruits|Northern hemisphere
Bilberry|Vaccinium myrtillus|Ericaceae|Berries & small fruits|Europe and northern Asia
Lingonberry|Vaccinium vitis-idaea|Ericaceae|Berries & small fruits|Northern hemisphere
Bearberry|Arctostaphylos uva-ursi|Ericaceae|Wild & woodland fruits|Northern hemisphere
Cranberry viburnum|Viburnum opulus|Adoxaceae|Wild & woodland fruits|Europe and northern Asia
Mayhaw|Crataegus aestivalis|Rosaceae|Wild & woodland fruits|Southeastern United States
Pawpaw berry|Asimina triloba|Annonaceae|Pomes & temperate fruits|Eastern North America
Chokeberry|Aronia melanocarpa|Rosaceae|Berries & small fruits|Eastern North America
Hackberry fruit|Celtis australis|Cannabaceae|Wild & woodland fruits|Mediterranean and western Asia
Strawberry tree fruit|Arbutus unedo|Ericaceae|Wild & woodland fruits|Mediterranean region
Madroño|Arbutus unedo|Ericaceae|Wild & woodland fruits|Mediterranean region
Yew aril|Taxus baccata|Taxaceae|Wild & woodland fruits|Europe and western Asia
Juniper berry|Juniperus communis|Cupressaceae|Wild & woodland fruits|Northern hemisphere
Rose hip fruit|Rosa rugosa|Rosaceae|Wild & woodland fruits|East Asia
Cloudberry fruit|Rubus chamaemorus|Rosaceae|Berries & small fruits|Arctic and boreal regions
Huckleberry|Gaylussacia baccata|Ericaceae|Berries & small fruits|Eastern North America
Bilimbi fruit|Averrhoa bilimbi|Oxalidaceae|Tropical & subtropical fruits|Southeast Asia
Tropical almond|Terminalia catappa|Combretaceae|Tropical & subtropical fruits|Indo-Pacific
Black plum|Syzygium cumini|Myrtaceae|Tropical & subtropical fruits|South Asia and Southeast Asia
African medlar|Vangueria infausta|Rubiaceae|Tropical & subtropical fruits|Southern Africa
Wild medlar|Vangueria infausta|Rubiaceae|Tropical & subtropical fruits|Southern Africa
Monkey orange|Strychnos spinosa|Loganiaceae|Tropical & subtropical fruits|Sub-Saharan Africa
Kei apple|Dovyalis caffra|Salicaceae|Tropical & subtropical fruits|Southern Africa
Natal plum|Carissa macrocarpa|Apocynaceae|Tropical & subtropical fruits|Southern Africa
Imbe|Garcinia livingstonei|Clusiaceae|Tropical & subtropical fruits|Southern Africa
Bacupari|Garcinia gardneriana|Clusiaceae|Tropical & subtropical fruits|South America
Yellow mombin|Spondias mombin|Anacardiaceae|Tropical & subtropical fruits|Tropical Americas
Ambarella|Spondias dulcis|Anacardiaceae|Tropical & subtropical fruits|Melanesia and Southeast Asia
Hog plum|Spondias mombin|Anacardiaceae|Tropical & subtropical fruits|Tropical Americas
June plum|Spondias dulcis|Anacardiaceae|Tropical & subtropical fruits|Melanesia and Southeast Asia
Olosapo|Couepia polyandra|Chrysobalanaceae|Tropical & subtropical fruits|Central America
Icaco|Chrysobalanus icaco|Chrysobalanaceae|Tropical & subtropical fruits|Tropical Americas and Africa
Cocoplum|Chrysobalanus icaco|Chrysobalanaceae|Tropical & subtropical fruits|Tropical Americas and Africa
Governor's plum|Flacourtia indica|Salicaceae|Tropical & subtropical fruits|Tropical Africa and Asia
Ramontchi|Flacourtia indica|Salicaceae|Tropical & subtropical fruits|Tropical Africa and Asia
Indian coffee plum|Flacourtia jangomas|Salicaceae|Tropical & subtropical fruits|South Asia and Southeast Asia
Muntingia|Muntingia calabura|Muntingiaceae|Tropical & subtropical fruits|Tropical America
Jamaica cherry|Muntingia calabura|Muntingiaceae|Tropical & subtropical fruits|Tropical America
Aratiles|Muntingia calabura|Muntingiaceae|Tropical & subtropical fruits|Tropical America
Ceylon olive|Elaeocarpus serratus|Elaeocarpaceae|Tropical & subtropical fruits|Sri Lanka and southern India
Rukam|Flacourtia rukam|Salicaceae|Tropical & subtropical fruits|Southeast Asia
Kundong|Garcinia parvifolia|Clusiaceae|Tropical & subtropical fruits|Borneo and Southeast Asia
Asam gelugur|Garcinia atroviridis|Clusiaceae|Tropical & subtropical fruits|Southeast Asia
Burmese grape fruit|Baccaurea ramiflora|Phyllanthaceae|Tropical & subtropical fruits|South and Southeast Asia
Pili fruit|Canarium ovatum|Burseraceae|Tropical & subtropical fruits|Philippines
Santol fruit|Sandoricum koetjape|Meliaceae|Tropical & subtropical fruits|Southeast Asia
Marang fruit|Artocarpus odoratissimus|Moraceae|Tropical & subtropical fruits|Borneo
Coconut apple|Cocos nucifera|Arecaceae|Palm & arid-region fruits|Indo-Pacific region
Screw pine fruit|Pandanus tectorius|Pandanaceae|Tropical & subtropical fruits|Indo-Pacific islands
Strawberry melon|Cucumis melo|Cucurbitaceae|Melons & gourds|Cultivated melon group
Casaba melon|Cucumis melo inodorus group|Cucurbitaceae|Melons & gourds|Cultivated melon group
Crenshaw melon|Cucumis melo inodorus group|Cucurbitaceae|Melons & gourds|Cultivated melon group
Christmas melon|Cucumis melo inodorus group|Cucurbitaceae|Melons & gourds|Cultivated melon group
Sharlyn melon|Cucumis melo|Cucurbitaceae|Melons & gourds|Cultivated melon group
Korean melon|Cucumis melo makuwa group|Cucurbitaceae|Melons & gourds|East Asia
Oriental melon|Cucumis melo makuwa group|Cucurbitaceae|Melons & gourds|East Asia
Gac fruit|Momordica cochinchinensis|Cucurbitaceae|Melons & gourds|Southeast Asia
Bitter melon fruit|Momordica charantia|Cucurbitaceae|Botanical fruits & unusual edibles|Tropical Africa and Asia
Cucumber fruit|Cucumis sativus|Cucurbitaceae|Botanical fruits & unusual edibles|South Asia
Pumpkin fruit|Cucurbita pepo|Cucurbitaceae|Botanical fruits & unusual edibles|North America
Winter squash fruit|Cucurbita maxima|Cucurbitaceae|Botanical fruits & unusual edibles|South America
Bottle gourd fruit|Lagenaria siceraria|Cucurbitaceae|Botanical fruits & unusual edibles|Africa
Snake gourd fruit|Trichosanthes cucumerina|Cucurbitaceae|Botanical fruits & unusual edibles|South and Southeast Asia
Ivy gourd fruit|Coccinia grandis|Cucurbitaceae|Botanical fruits & unusual edibles|Africa and Asia
Kantola fruit|Momordica dioica|Cucurbitaceae|Botanical fruits & unusual edibles|South Asia

'''.strip()

def slugify(s):
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
    s=re.sub(r'[^a-z0-9]+','-',s).strip('-')
    return s or 'fruit'

# common group notes for useful, general educational descriptions
GROUP_INFO = {
 'Pomes & temperate fruits': ('crisp or tender flesh, with flavors from floral-sweet to bright and tart', 'Many pome fruits contain water, dietary fibre and varying amounts of vitamin C and polyphenols.', 'Often eaten fresh, baked, poached, dried or fermented. Firmness and acidity help determine the best use.', 'Keep ripe fruit cool; some fruits continue to soften after harvest. Store away from strongly aromatic foods when flavour transfer is a concern.', 'Temperate trees and vines often depend on seasonal dormancy, suitable pollination and a climate-matched cultivar.'),
 'Stone fruits': ('juicy flesh surrounding a single hard pit, with aromas that range from honeyed to tangy', 'Stone fruits contribute water, fibre and a range of carotenoids or vitamin C depending on species and flesh colour.', 'Enjoy fresh, grilled, baked, poached, preserved or dried. The pit is not the edible flesh and should not be treated as food.', 'Ripen at room temperature when still firm, then refrigerate ripe fruit to slow softening.', 'Flowering time, late frost risk, pollination needs and disease pressure strongly influence orchard performance.'),
 'Berries & small fruits': ('bright, layered flavors that can be tart, fragrant, sweet or resinous', 'Many small fruits provide fibre and colourful plant compounds; nutrient levels vary with species and ripeness.', 'Use fresh, frozen, blended, baked, dried or preserved. Small fruits can bruise quickly and often benefit from gentle handling.', 'Refrigerate delicate berries dry and wash just before eating; freeze surplus promptly for longer storage.', 'Harvest timing is often more important than size: fruit should be picked at the flavour and colour stage characteristic of the species.'),
 'Grapes & vine fruits': ('juicy berries with sweetness, acidity, perfume and skin texture that vary widely', 'Grapes provide water and carbohydrates; dark-skinned types contain pigments such as anthocyanins.', 'Eat fresh, dry as raisins, press for juice, or ferment where appropriate. Seed, skin and acidity affect the best use.', 'Keep bunches cool and dry; remove damaged berries and avoid washing until use.', 'Vine management, sunlight exposure, water balance and harvest maturity all shape flavour.'),
 'Citrus fruits': ('aromatic zest, juicy segments and a balance of acidity, bitterness and sweetness', 'Citrus is widely known for vitamin C; the peel also contains aromatic oils, while fibre content depends on what is eaten.', 'Use segments, juice, zest, marmalade, marinades and candied peel. Peel oils can be intense, so use zest in measured amounts.', 'Store in a cool, ventilated place for short periods or refrigerate to extend freshness; avoid trapping damp fruit in sealed bags.', 'Citrus trees are sensitive to cold and are commonly propagated by grafting to preserve cultivar traits.'),
 'Tropical & subtropical fruits': ('a broad spectrum from floral and creamy to resinous, tangy, musky or intensely sweet', 'These fruits can contribute vitamin C, carotenoids, folate, potassium or fibre, but profiles differ greatly between species.', 'Eat ripe flesh fresh, blend into drinks, cook in curries and sauces, dry, pickle or preserve where customary.', 'Ripening behaviour differs: some fruits soften after picking while others develop best flavour on the plant. Check each species separately.', 'Heat, rainfall seasonality, elevation and local pollinators shape cultivation; tropical species are not all suited to the same climate.'),
 'Cacti & dryland fruits': ('crisp, juicy or seed-speckled flesh with refreshing acidity and mild sweetness', 'Many dryland fruits contain water and fibre; vivid flesh colours may reflect natural pigments.', 'Eat fresh or chilled, blend, dry or turn into syrups and preserves. Handle spiny skins carefully and remove glochids where present.', 'Cool ripe fruits and protect cut flesh from drying; process seed-rich fruits carefully.', 'Adaptations to arid environments do not mean every cactus fruit can tolerate every dry climate; species and water needs differ.'),
 'Melons & gourds': ('cool, refreshing flesh with aroma and sweetness that depend strongly on maturity', 'Melons provide water; orange-fleshed types often contain carotenoids, while amounts vary with cultivar and ripeness.', 'Serve chilled, in salads, smoothies, desserts or savoury dishes. Some botanical fruits in this group are usually cooked rather than eaten sweet.', 'Whole melons keep differently from cut melons. Refrigerate cut pieces promptly and use clean utensils.', 'Warmth, sunlight, pollination, spacing and water management influence fruit set, sweetness and texture.'),
 'Pomegranates & figs': ('dense sweetness, seed crunch, soft pulp or juicy arils with distinctive texture', 'Pomegranates and figs provide fibre and plant compounds; the edible portions and nutrient profiles differ markedly.', 'Eat fresh, pair with savoury dishes, dry figs, press juice or use arils as a garnish.', 'Store intact pomegranates and figs in cool conditions; fresh figs are especially perishable.', 'Figs have a specialised flower structure, while pomegranates develop many seeds surrounded by juicy arils.'),
 'Palm & arid-region fruits': ('fibrous, starchy, syrupy or chewy textures, sometimes with caramel-like notes', 'Nutrient patterns vary widely; date flesh is carbohydrate-rich, while coconut flesh contains substantial fat.', 'Eat fresh where customary, dry, press, ferment or cook. Some palm fruits have hard seeds or protective fibres that must be removed.', 'Drying and cool storage can extend shelf life; moisture and mould control matter for dried products.', 'Palms can support important food systems in drylands, tropical islands and riverine habitats.'),
 'Wild & woodland fruits': ('often sharper, more astringent or more aromatic than supermarket fruit', 'Wild fruits can provide fibre and varied plant compounds, but edibility is species-specific and identification matters.', 'Use only after confident identification and local guidance. Some species require cooking or processing; others are not edible.', 'Wild harvest should be handled gently and kept separate from uncertain or damaged specimens.', 'Wild populations support wildlife and genetic diversity; harvest sustainably and avoid damaging plants or habitats.'),
 'Botanical fruits & unusual edibles': ('flavors and textures that may differ from the everyday culinary idea of a fruit', 'Nutrient profiles depend on the plant and the edible part; botanical fruit status does not automatically mean a part is safe to eat.', 'Some are culinary vegetables, spices or nuts in everyday use even though the plant part is botanically a fruit.', 'Follow species-specific food preparation and storage guidance rather than assuming all fruits are eaten raw.', 'Botanical fruits develop from flowering plants and can include berries, capsules, legumes, pepos, drupes and other fruit types.'),
}

species=[]
for line in ROWS.splitlines():
    if not line.strip(): continue
    fields=line.strip().split('|')
    if len(fields)!=5: continue
    name, sci, family, group, origin = [x.strip() for x in fields]
    # Deduplicate repeated common-name rows, keeping the first high-quality form.
    slug=slugify(name)
    if any(s['slug']==slug for s in species):
        continue
    info=GROUP_INFO.get(group, GROUP_INFO['Tropical & subtropical fruits'])
    flavor, nutrition, uses, storage, growing = info
    wiki = name.replace(' fruit','').replace('Citrus orange','Orange')
    if name == 'Dragon fruit':
        wiki = 'Dragon fruit'
    if name in ('Meyer lemon','Key lime','Blood orange','Yellow dragon fruit','Red dragon fruit'):
        wiki = name
    species.append({
      'slug':slug,'name':name,'scientificName':sci,'family':family,'group':group,
      'origin':origin,'recordType':'Species profile','parentSlug':None,
      'summary':f'{name} is part of the world’s broad edible-fruit diversity. Its flavour and texture reflect species biology, growing conditions, maturity and the way the fruit is handled after harvest.',
      'uniqueness':f'What stands out about {name.lower()} is the combination of plant lineage, edible structure and regional food traditions. Names and forms can overlap across languages and markets, so scientific naming helps distinguish similar fruits.',
      'flavor':flavor,'texture':'Texture depends on maturity and cultivar; ripe flesh may be firm, crisp, soft, fibrous, creamy or juicy.',
      'colour':'Colour varies by species, cultivar and maturity; peel colour does not always indicate sweetness or ripeness.',
      'season':'Season varies by hemisphere, local climate and cultivar; in many regions fruit is available for a short harvest window.',
      'nutrition':nutrition,'uses':uses,'storage':storage,'growing':growing,
      'benefits':['Contributes variety, flavour and texture to a balanced eating pattern.','May provide water, dietary fibre and micronutrients depending on the fruit and portion.','Offers a way to explore regional food cultures and plant diversity.'],
      'caution':'Nutrition and tolerance vary by person, species and preparation. Fruit is food, not a medical treatment. For wild or unfamiliar fruits, confirm identification and safe preparation before eating.',
      'wikiTitle':wiki,'image':None,'tags':[group.split('&')[0].strip(),family,'fruit profile']
    })

# Fruit-specific image selection uses external photo assets as a visual fallback; the
# front-end tries the corresponding Wikipedia summary image when one is available.
IMAGE_URLS = {
 'default':'https://images.unsplash.com/photo-1619566636858-adf3ef46400b?auto=format&fit=crop&w=1200&q=85',
 'Citrus fruits':'https://images.unsplash.com/photo-1547514701-42782101795e?auto=format&fit=crop&w=1200&q=85',
 'Berries & small fruits':'https://images.unsplash.com/photo-1601004890684-d8cbf643f5f2?auto=format&fit=crop&w=1200&q=85',
 'Tropical & subtropical fruits':'https://images.unsplash.com/photo-1490474418585-ba9bad8fd0ea?auto=format&fit=crop&w=1200&q=85',
 'Melons & gourds':'https://images.unsplash.com/photo-1571575173700-afb9492e6a50?auto=format&fit=crop&w=1200&q=85',
 'Pomes & temperate fruits':'https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?auto=format&fit=crop&w=1200&q=85',
 'Stone fruits':'https://images.unsplash.com/photo-1629828874514-c1e5103fca1f?auto=format&fit=crop&w=1200&q=85',
 'Grapes & vine fruits':'https://images.unsplash.com/photo-1537640538966-79f369143f8f?auto=format&fit=crop&w=1200&q=85',
 'Pomegranates & figs':'https://images.unsplash.com/photo-1541344999736-83eca272f6fc?auto=format&fit=crop&w=1200&q=85',
 'Palm & arid-region fruits':'https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?auto=format&fit=crop&w=1200&q=85',
 'Cacti & dryland fruits':'https://images.unsplash.com/photo-1550258987-190a2d41a8ba?auto=format&fit=crop&w=1200&q=85',
 'Wild & woodland fruits':'https://images.unsplash.com/photo-1498557850523-fd3d118b962e?auto=format&fit=crop&w=1200&q=85',
 'Botanical fruits & unusual edibles':'https://images.unsplash.com/photo-1611080626919-7cf5a9dbab5b?auto=format&fit=crop&w=1200&q=85'
}
for s in species:
    s['image']=IMAGE_URLS.get(s['group'],IMAGE_URLS['default'])

# Species-specific editorial notes for widely encountered fruits. These are deliberately
# qualitative and avoid unsourced nutrient quantities, medical effects, or fixed harvest dates.
FRUIT_FACTS = {
 'apple': {
  'summary':'Apple is a pome fruit with crisp or tender flesh and a huge range of cultivated forms. Texture, acidity, aroma and storage life can vary noticeably among cultivars.',
  'uniqueness':'An apple is a pome: much of the familiar eating flesh develops from floral tissues surrounding the ovary. Apples have a long history of selection from Central Asian ancestry, and thousands of named forms have been recorded across food cultures.',
  'flavor':'Flavour can range from honeyed and mild to sharp, aromatic, tannic or wine-like; sweetness and acidity should be considered together.',
  'texture':'The flesh may be exceptionally crisp, dense, fine-grained, tender or juicy, with changes during storage.',
  'colour':'Skin may be green, yellow, striped, blush-red or fully red; russeting is normal in many cultivars.',
  'season':'In temperate regions, harvest often runs from late summer into autumn, but early and late cultivars extend the window.',
  'nutrition':'Apples contribute water and dietary fibre, including fibre concentrated in the edible skin and flesh. Composition varies with cultivar, size and storage.',
  'uses':'Common uses include fresh eating, baking, sauces, juice, cider, drying and preserving. High-acid or firm-fleshed cultivars may behave differently in cooking.',
  'storage':'Many apple cultivars store well under cool conditions. Keep bruised fruit separate and check stored apples regularly for soft spots or decay.',
  'growing':'Flowering time, winter chill, compatible pollination partners and fire-blight or scab pressure are important when choosing a cultivar.'
 },
 'mango': {
  'summary':'Mango is a tropical stone fruit known for fragrant flesh and extraordinary cultivar diversity. Colour, fibre, size and season vary widely, even among fruits sold simply as mangoes.',
  'uniqueness':'Mango is a drupe with a single large, flattened stone. It has deep roots in South Asian cultivation and has spread into many tropical growing regions, where local selections reflect climate, taste and harvest traditions.',
  'flavor':'Ripe mango may taste floral, resinous, citrus-like, honeyed or peach-like, with acidity and aroma varying among cultivars.',
  'texture':'Flesh can be silky and fibre-light or noticeably fibrous; maturity strongly affects juiciness and softness.',
  'colour':'The peel may be green, yellow, orange, red or mottled. Peel colour alone is not a dependable test of ripeness.',
  'season':'Harvest seasons depend on flowering flush, cultivar, rainfall and hemisphere. Regional calendars are more useful than a single global month.',
  'nutrition':'Mango contributes water, fibre and vitamins such as vitamin C; orange-yellow flesh can contain carotenoid pigments. Amounts vary by variety and serving.',
  'uses':'Eat ripe flesh fresh, blend into drinks, add to salads and savoury dishes, dry, pickle green fruit or preserve chutneys and sauces.',
  'storage':'Firm fruit may soften at room temperature; refrigerate once ripe. Avoid crushing the fruit and use cut mango promptly under refrigeration.',
  'growing':'Mango trees favour warm conditions and good drainage. Flowering and fruit set can be affected by humidity, rain, temperature and local disease pressure.'
 },
 'banana': {
  'summary':'Banana is a versatile fruit crop with dessert and cooking types ranging from small aromatic fingers to starchy plantains. Many familiar edible bananas have little or no hard seed.',
  'uniqueness':'Botanically, a banana is a berry that develops in a cluster called a hand. Most widely sold dessert bananas are cultivated forms selected for edible flesh and are propagated vegetatively to maintain their traits.',
  'flavor':'Dessert types become sweeter as starch converts to sugars; cooking bananas may stay firmer and starchier until prepared.',
  'texture':'Texture ranges from creamy and soft to dense, dry or starchy depending on cultivar and maturity.',
  'colour':'Peel can be green, yellow, red, purple or mottled. Some cultivars remain partly green even when ready to eat.',
  'season':'In warm growing regions, harvest can be spread across much of the year; local supply depends on planting cycles and cultivar.',
  'nutrition':'Bananas provide carbohydrates, water and some fibre, with potassium among their familiar mineral contributions. Ripeness changes the balance of starch and sugars.',
  'uses':'Ripe bananas are eaten fresh, blended or baked; plantains and other cooking types are commonly boiled, steamed, fried or roasted.',
  'storage':'Let green fruit ripen at room temperature. Refrigeration can darken the peel while the flesh remains usable; keep cut fruit covered and chilled.',
  'growing':'Bananas are large herbaceous plants rather than woody trees. Warmth, moisture, wind protection and healthy planting material matter for reliable bunches.'
 },
 'sweet orange': {
  'summary':'Sweet orange is a citrus fruit with juicy segments enclosed by a fragrant peel. Cultivars differ in seed number, rind thickness, juice quality and flesh pigmentation.',
  'uniqueness':'Citrus fruits have a specialised segmented interior and an oil-rich outer peel. Sweet oranges are cultivated in many climates, and blood-orange types can develop red pigments under suitable conditions.',
  'flavor':'The classic profile balances sweetness with fresh acidity; aroma compounds in the peel add a bright citrus note.',
  'texture':'Juicy vesicles fill the segments, while peel thickness and the ease of separating the rind vary by cultivar.',
  'colour':'Flesh is usually orange, while selected blood oranges can develop red or burgundy tones; peel colour may not perfectly reflect internal maturity.',
  'season':'Season differs by hemisphere and cultivar, with early, mid-season and late selections extending harvest.',
  'nutrition':'Oranges are well known for vitamin C and also contribute water and fibre when eaten as whole segments.',
  'uses':'Eat segments fresh, squeeze juice, use zest, make marmalade or add citrus to dressings and desserts.',
  'storage':'Store in cool, ventilated conditions or refrigerate to extend freshness. Avoid sealing damp fruit in a bag for long periods.',
  'growing':'Citrus trees generally prefer warmth, sunlight and drainage. Cold tolerance differs considerably, and grafted rootstocks influence orchard performance.'
 },
 'lemon': {
  'summary':'Lemon is an aromatic citrus fruit prized for sour juice and fragrant peel. Its acidity makes it useful as a flavouring ingredient even in small quantities.',
  'uniqueness':'The lemon combines high-acid juice with a peel rich in volatile oils. Cultivars differ in seed number, rind thickness, fruit shape and whether they produce several flowering flushes.',
  'flavor':'Juice is distinctly acidic, with floral and fresh citrus aromas; peel zest adds fragrant oils rather than the same sharpness as the juice.',
  'texture':'The rind can be thin or thick, and the interior contains juicy segments separated by membranes.',
  'colour':'Mature peel often turns yellow, but colour changes with temperature and cultivar and is not a perfect ripeness test.',
  'season':'Many lemon trees can flower and fruit in more than one flush, so supply can be less concentrated than for some temperate fruits.',
  'nutrition':'Lemon juice contributes vitamin C in quantities that depend on the fruit and serving; zest contributes aroma and should be used in moderate amounts.',
  'uses':'Use juice and zest in dressings, sauces, preserves, drinks and baking. Acid can brighten a dish and slow browning on some cut produce.',
  'storage':'Keep fruit cool and avoid letting cut surfaces dry. Refrigeration can extend usable life compared with a hot countertop.',
  'growing':'Lemons favour warm, sunny, well-drained sites and are sensitive to frost. Container culture can help in cooler climates if light and winter protection are adequate.'
 },
 'pineapple': {
  'summary':'Pineapple is a tropical multiple fruit formed as many small fruitlets fuse around a central axis. It combines sweet-acid flesh with a tough patterned skin and a leafy crown.',
  'uniqueness':'What looks like one pineapple develops from an inflorescence: individual flowers contribute fruitlets that merge into the mature structure. The crown and side shoots can be used for vegetative propagation.',
  'flavor':'A ripe pineapple balances sweetness and acidity with a recognisable tropical aroma; maturity and cultivar affect juiciness.',
  'texture':'Flesh is juicy and fibrous, with a firmer core and softer outer portions depending on fruit and cultivar.',
  'colour':'The flesh may be pale yellow to golden, while the outside can show green, bronze or yellow tones at maturity.',
  'season':'Warm climates may support staggered production, but harvest timing depends on cultivar, planting schedule and local growing conditions.',
  'nutrition':'Pineapple provides water, fibre and vitamin C. Nutrient levels vary by maturity, portion and processing.',
  'uses':'Serve fresh, grill, cook into savoury dishes, blend into drinks or preserve. Heat and processing change texture and flavour.',
  'storage':'Keep whole fruit in a cool place for a short period or refrigerate; cut pineapple should be covered and chilled promptly.',
  'growing':'Pineapple is a ground-growing bromeliad, not a tree. It prefers warmth, sunlight and well-drained soil and is sensitive to frost and waterlogging.'
 },
 'avocado': {
  'summary':'Avocado is a fruit with creamy flesh and a large seed. Cultivars vary in skin texture, size, harvest timing and the balance of water and oil in the edible portion.',
  'uniqueness':'Avocado is botanically a berry with one large seed, though its thick flesh and savoury use make it unusual among familiar fruits. Many cultivars are grafted to preserve a predictable harvest and eating quality.',
  'flavor':'The flavour is generally mild, nutty or buttery, allowing avocado to work in savoury dishes as well as some sweet preparations.',
  'texture':'Ripe flesh is creamy and soft; firmness and smoothness depend on cultivar and maturity.',
  'colour':'Skin may be green, purple or nearly black, and some cultivars change colour as they ripen while others do not.',
  'season':'Harvest windows vary by cultivar and region. Some avocado cultivars mature on the tree but soften after picking.',
  'nutrition':'Avocado contributes dietary fibre and contains notable amounts of fat, predominantly unsaturated. Composition varies with cultivar and serving size.',
  'uses':'Mash for spreads, add to salads and savoury dishes, blend into sauces or use as a creamy ingredient.',
  'storage':'Firm fruit can soften at room temperature. Once ripe, refrigerate; cover cut flesh to limit drying and browning.',
  'growing':'Avocado trees need excellent drainage and climate-matched selections. Pollination type, cold tolerance, root health and mature canopy size are important.'
 },
 'watermelon': {
  'summary':'Watermelon is a large pepo with refreshing watery flesh and seeds that may be dark, pale or absent in some cultivated types. Flesh colour includes red, pink, orange and yellow forms.',
  'uniqueness':'Watermelon belongs to the gourd family and develops from an inferior ovary into a thick-rinded fruit. Its internal colour and seed pattern vary widely among cultivated forms.',
  'flavor':'Good maturity often brings sweetness with a clean, refreshing finish; flavour can be mild or intensely sweet depending on the selection.',
  'texture':'Flesh is juicy and crisp to tender, with texture affected by harvest maturity and storage.',
  'colour':'Red is common, but orange and yellow flesh also occur. Rind pattern and colour differ by cultivar.',
  'season':'Watermelon is typically associated with warm-season harvests, although timing varies with region and protected cultivation.',
  'nutrition':'Watermelon is water-rich and provides some fibre; red-fleshed types contain the pigment lycopene. The amounts vary with variety and serving.',
  'uses':'Eat chilled, add to salads, blend into drinks or grill thick slices. Seeds and rind have traditional culinary uses in some regions.',
  'storage':'Keep whole fruit in a suitable cool place; refrigerate cut pieces promptly in clean covered containers.',
  'growing':'Watermelon vines need warmth, space, pollination and a long enough season for fruit to mature. Water management can affect cracking and quality.'
 },
 'strawberry': {
  'summary':'Strawberry is an aggregate accessory fruit with tiny dry fruits, called achenes, visible across the outside. Cultivars vary in aroma, softness, colour and repeat-fruiting habit.',
  'uniqueness':'The red fleshy part of a strawberry is a swollen flower receptacle; the tiny seed-like achenes on its surface are the true individual fruits. This unusual structure makes strawberry a classic botanical example.',
  'flavor':'Aroma can be floral, candy-like, citrusy or deeply jammy; acidity and sweetness vary by cultivar and maturity.',
  'texture':'Flesh may be firm and transport-friendly or very soft and fragrant, with ripe berries bruising easily.',
  'colour':'Most familiar cultivars are red, but white, pale pink and yellowish forms are also grown.',
  'season':'Harvest can be concentrated or repeat through the growing season depending on day length, cultivar and growing system.',
  'nutrition':'Strawberries provide vitamin C, water and fibre; the amount per serving varies with maturity and portion size.',
  'uses':'Eat fresh, freeze, bake, make jams, sauces and desserts, or add to salads.',
  'storage':'Refrigerate dry and unwashed until use, remove damaged berries and wash gently just before eating.',
  'growing':'Strawberries are low-growing perennial plants. Cultivars differ in day-length response, disease tolerance, runner production and suitability for containers.'
 },
 'blueberry': {
  'summary':'Blueberries are small fruits of the genus Vaccinium, often coated with a pale waxy bloom. Types range from low-growing wild plants to vigorous highbush cultivars.',
  'uniqueness':'The natural whitish bloom on many blueberries is a surface wax, not dust. Wild and cultivated blueberries differ in growth habit, berry size, harvest pattern and local adaptation.',
  'flavor':'Flavour ranges from bright and tart to mild and very sweet, with floral notes that vary by cultivar.',
  'texture':'The skin provides a gentle snap around juicy flesh; berry firmness influences handling and storage.',
  'colour':'Deep blue or blue-purple skins are common, though other Vaccinium species can produce red or dark berries.',
  'season':'Harvest timing depends on species, cultivar and climate; early, mid- and late selections spread the harvest.',
  'nutrition':'Blueberries provide water, fibre and pigments such as anthocyanins. No single colour or cultivar guarantees a specific health effect.',
  'uses':'Eat fresh, freeze, bake into pastries, add to porridge or prepare sauces and preserves.',
  'storage':'Keep berries cool and dry, remove damaged fruit and wash shortly before eating. Freezing is useful for seasonal surplus.',
  'growing':'Many blueberries require acidic soil and consistent moisture with good drainage. Chill needs and heat tolerance vary among highbush, lowbush and rabbiteye types.'
 },
 'grape': {
  'summary':'Grape is a vine fruit with cultivars for fresh eating, drying, juice and fermentation. Berry colour, seed content, skin thickness and aroma can vary dramatically.',
  'uniqueness':'Grape berries grow in clusters, and their skins contain compounds that shape colour and flavour. The same broad crop includes table, raisin and wine selections with different harvest targets.',
  'flavor':'Flavour can be neutral and crisp, intensely muscat-like, floral, spicy or tart, depending on species and cultivar.',
  'texture':'Berries may have crisp or tender flesh, thick or thin skins, and seeds or no substantial seeds.',
  'colour':'Green, gold, red, blue and nearly black cultivars are common; berry colour changes during maturation.',
  'season':'Many table and wine grapes are harvested from summer into autumn in their growing regions, with timing strongly cultivar-dependent.',
  'nutrition':'Grapes provide water and carbohydrates; dark skins contain anthocyanin pigments. Seed and skin composition varies by cultivar.',
  'uses':'Eat fresh, dry as raisins, press for juice or use wine grapes for fermentation where appropriate.',
  'storage':'Keep bunches cool and dry, remove damaged berries and avoid washing until serving.',
  'growing':'Vines require sunlight, structural support, pruning and a suitable climate. Humidity and rainfall can influence disease management and fruit quality.'
 },
 'pomegranate': {
  'summary':'Pomegranate contains many juicy seed coverings, called arils, enclosed by a leathery rind. Cultivars differ in aril colour, seed hardness, acidity and sweetness.',
  'uniqueness':'The edible arils are juicy coverings surrounding individual seeds, arranged in chambers separated by pale membranes. This structure gives pomegranate its distinctive way of eating and preparing.',
  'flavor':'Arils may be tart, wine-like, sweet or balanced; perceived flavour is strongly influenced by acidity.',
  'texture':'Juicy arils contrast with crunchy seeds, though seed hardness varies among cultivars.',
  'colour':'Rind can be yellow, pink, orange or deep red; arils range from pale pink to ruby. External colour is not a perfect indicator of internal taste.',
  'season':'Harvest often follows warm growing seasons, but cultivar, local climate and irrigation affect timing.',
  'nutrition':'Pomegranate arils provide water, fibre and plant pigments. Nutrient amounts vary by variety and edible portion.',
  'uses':'Eat arils fresh, garnish savoury dishes, press juice or use in sauces and preserves.',
  'storage':'Intact fruit can keep for some time in cool conditions. Refrigerate arils once separated and use clean tools to avoid contamination.',
  'growing':'Pomegranates favour sunny conditions and well-drained soil. Some cultivars tolerate heat and dryness better than others.'
 },
 'fig': {
  'summary':'Fig has a soft, often sweet interior held inside a thin skin. The structure is a syconium—an enclosed cluster of tiny flowers—rather than a simple hollow fruit.',
  'uniqueness':'A fig is an inflorescence enclosed within a fleshy structure, with many tiny flowers developing inside. Fig pollination biology differs among types and growing regions, which is why cultivar choice matters.',
  'flavor':'Flavour ranges from honeyed and floral to berry-like, jammy or gently nutty.',
  'texture':'The skin can be delicate and the interior soft, with numerous small seeds adding texture.',
  'colour':'Figs may be green, yellow, bronze, purple or nearly black, with pale or richly coloured flesh.',
  'season':'Many fig cultivars produce one main crop and some also produce an earlier crop; regional conditions govern timing.',
  'nutrition':'Fresh figs provide water and fibre; dried figs are more concentrated because much of their water has been removed.',
  'uses':'Eat fresh when ripe, dry, bake, poach or pair with cheese and savoury foods.',
  'storage':'Fresh figs are delicate and highly perishable; refrigerate ripe fruit and handle without squeezing.',
  'growing':'Figs favour sun and drainage. Cold hardiness, crop pattern and whether pollination is needed vary by type and cultivar.'
 },
 'lychee': {
  'summary':'Lychee has a rough pink-red rind surrounding translucent, fragrant flesh and a single seed. Freshness and careful harvest help preserve its delicate aroma.',
  'uniqueness':'The leathery, bumpy rind protects a translucent aril that surrounds the seed. Lychee is strongly associated with subtropical Asian growing traditions and is often harvested in a relatively short season.',
  'flavor':'The flesh is floral and sweet, sometimes described as rose-like or muscat-like, with a refreshing finish.',
  'texture':'The translucent flesh is juicy and tender, while the seed is not eaten.',
  'colour':'The rind is often red or pink at harvest, but colour changes quickly after picking and is not a complete measure of quality.',
  'season':'Harvest is often concentrated in a short warm-season window and differs by cultivar and region.',
  'nutrition':'Lychee provides water and vitamin C; amounts vary with maturity and serving size.',
  'uses':'Eat the peeled aril fresh, chill for serving, or use in fruit salads and desserts.',
  'storage':'Keep cool and handle gently; the rind can brown during storage even when the flesh remains usable.',
  'growing':'Lychee prefers humid subtropical conditions with a suitable seasonal temperature pattern; young trees can be sensitive to cold and dry winds.'
 },
 'dragon fruit': {
  'image':'https://upload.wikimedia.org/wikipedia/commons/c/c5/Dragon_fruit.JPG',
  'summary':'Dragon fruit is the edible fruit of climbing cactus species, with bold skin bracts and flesh that may be white, red or purple. It is also known as pitaya.',
  'uniqueness':'Dragon fruit comes from climbing cacti whose large flowers often open at night. Flowering, pollination compatibility and the need for hand pollination can affect fruit set.',
  'flavor':'The taste is usually mild and refreshing, with sweetness and acidity varying by species and maturity.',
  'texture':'Soft juicy flesh contains many tiny edible seeds that give a light crunch.',
  'colour':'Skin is commonly pink or yellow, while flesh may be white, red or purple depending on the species.',
  'season':'In warm regions, repeated flowering flushes can produce more than one harvest period.',
  'nutrition':'Dragon fruit provides water and fibre; flesh colour and nutrient composition vary among species and cultivars.',
  'uses':'Eat chilled with a spoon, add to fruit salads or blend into drinks and desserts.',
  'storage':'Refrigerate ripe fruit and keep cut flesh covered. Use clean utensils when cutting and serving.',
  'growing':'Dragon fruit needs a strong support structure, warmth and good drainage. Cold, waterlogging and pollination limitations can reduce production.'
 },
 'jackfruit': {
  'summary':'Jackfruit is a very large multiple fruit that develops from many flowers. Ripe bulbs are sweet, while immature flesh is used as a savoury ingredient in several regional cuisines.',
  'uniqueness':'Jackfruit can become one of the largest fruits produced by a tree. Each bulb is part of a larger fruit structure, and the crop is used at very different maturity stages for sweet and savoury dishes.',
  'flavor':'Ripe bulbs are sweet and strongly aromatic, with flavours that may recall banana, pineapple or other tropical fruit.',
  'texture':'Ripe bulbs are fleshy and can be soft or firm; immature flesh is fibrous and takes on seasoning in cooked dishes.',
  'colour':'Ripe bulbs range from pale yellow to deep golden or orange; peel stays green to yellow-brown as maturity advances.',
  'season':'Harvest depends on tropical rainfall patterns, flowering flushes and local selections.',
  'nutrition':'Jackfruit contributes carbohydrates, fibre and some micronutrients; ripe and immature fruit are used differently and have different composition.',
  'uses':'Eat ripe bulbs fresh or in desserts; cook immature flesh in curries and savoury preparations. Seeds are eaten after suitable cooking in some traditions.',
  'storage':'Whole fruit is bulky and can deteriorate after damage. Clean and chill cut bulbs promptly; use a food-safe method for handling sticky latex.',
  'growing':'Jackfruit trees need warm conditions, room for a large canopy and suitable drainage. Mature fruit weight makes harvest planning important.'
 },
 'durian': {
  'summary':'Durian is a large, spiny tropical fruit with creamy edible arils and a strong distinctive aroma. Cultivars vary in bitterness, sweetness, texture and seed size.',
  'uniqueness':'A thick spiny rind protects several chambers of pale to golden edible arils. The aroma is unusually powerful and strongly polarising, making durian one of the most recognisable tropical fruits.',
  'flavor':'Flavour can be custardy, onion-like, nutty, caramel-like or bitter-sweet depending on cultivar and maturity.',
  'texture':'Arils range from firm and dense to soft and creamy, with a large seed inside.',
  'colour':'The edible flesh is often pale cream to deep yellow or orange; rind colour and spine pattern vary by species and cultivar.',
  'season':'Many production regions have seasonal harvest peaks tied to rainfall and flowering; timing differs across Southeast Asia.',
  'nutrition':'Durian is energy-dense compared with many watery fruits and provides carbohydrates and some fat; amounts differ by cultivar and portion.',
  'uses':'Eat the arils fresh, frozen or in desserts and regional preparations. The seeds require appropriate cooking if used as food.',
  'storage':'Keep whole fruit in suitable conditions and follow local food-handling advice. Refrigerate edible arils in clean covered containers.',
  'growing':'Durian trees prefer warm, humid tropical environments and deep, well-drained soil. Pollination, rainfall and cultivar all affect yield.'
 },
 'avocado': {},
 'guava': {
  'summary':'Guava is an aromatic tropical fruit with seed-rich flesh and substantial variation in skin and pulp colour. White, cream, pink and red-fleshed cultivars are grown.',
  'uniqueness':'Guava belongs to the myrtle family and is known for a distinctive musky fragrance. Its small hard seeds are embedded in the central pulp, while fruit colour and texture differ by cultivar.',
  'flavor':'Ripe guava can taste floral, musky, sweet and gently tart, with scent ranging from delicate to intense.',
  'texture':'Flesh may be soft and creamy or firm and crunchy; seeds can be prominent in the centre.',
  'colour':'Skin is often green to yellow; flesh may be white, cream, pink, salmon or red.',
  'season':'Fruit may be produced in seasonal flushes or across a long period in warm climates, depending on cultivar and pruning.',
  'nutrition':'Guava is known for vitamin C and also contributes fibre; composition varies with cultivar and maturity.',
  'uses':'Eat ripe fruit fresh, blend into drinks, cook into pastes and jams, or use in savoury sauces.',
  'storage':'Ripen firm fruit at room temperature, then refrigerate once ready. Handle carefully because ripe fruit softens quickly.',
  'growing':'Guava tolerates a range of tropical and subtropical conditions, though frost, drainage, pests and local disease pressure still matter.'
 },
 'kiwifruit': {
  'summary':'Kiwifruit is a berry produced by Actinidia vines. Commercial types range from fuzzy brown-skinned green fruit to smooth or golden-fleshed selections.',
  'uniqueness':'Kiwifruit develops on woody climbing vines and is botanically a berry. The genus includes fuzzy, smooth, hardy and ornamental species with different cold tolerances and fruit traits.',
  'flavor':'Green kiwifruit often balances tartness with sweetness, while gold types can taste sweeter and more tropical; cultivar differences are substantial.',
  'texture':'The flesh is juicy and dotted with small edible seeds; firmness changes noticeably during ripening.',
  'colour':'Skin can be fuzzy brown or smoother green-brown, while flesh ranges from green to gold and sometimes red-tinged.',
  'season':'Harvest timing depends on cultivar and hemisphere; fruit can be stored after picking under suitable conditions.',
  'nutrition':'Kiwifruit contributes vitamin C, fibre and water; the profile varies between species, cultivars and serving sizes.',
  'uses':'Eat with a spoon or peeled and sliced, add to fruit salads or use in sauces and desserts.',
  'storage':'Allow firm kiwifruit to soften as appropriate; keep ripe fruit cool. Avoid storing cut pieces for long periods at room temperature.',
  'growing':'Actinidia vines need a suitable climate, support and often separate male and female plants unless the cultivar is self-fertile.'
 },
 'pomegranate': {},
 'fig': {},
 'starfruit': {
  'summary':'Starfruit, also called carambola, is a ridged tropical fruit that forms a star-shaped cross-section when sliced. Its flavour can be crisp, lightly sweet and tart.',
  'uniqueness':'The five prominent longitudinal ridges create the characteristic star shape. The fruit is eaten with its thin skin and is commonly used as a garnish as well as a fresh fruit.',
  'flavor':'Flavour ranges from citrus-like and tart to lightly sweet, depending on cultivar and maturity.',
  'texture':'Flesh is crisp and juicy, with thin edible skin and small seeds in some ridges.',
  'colour':'The fruit changes from green to yellow-green or golden as it matures; the ridges may brown after handling.',
  'season':'Warm climates can produce fruit in repeated flushes; harvest depends on local flowering and rainfall.',
  'nutrition':'Starfruit contributes water and some fibre and micronutrients; nutrient content varies with maturity and portion.',
  'uses':'Slice crosswise for fresh eating, salads and garnish, or use in juices and preserves.',
  'storage':'Handle ripe fruit carefully so the ridges are not bruised. Refrigerate ripe fruit and wash before slicing.',
  'growing':'Carambola prefers warm, humid conditions and protection from frost. Drainage, water availability and cultivar influence fruit quality.'
 },
 'tamarind': {
  'summary':'Tamarind is a pod fruit with sticky brown pulp surrounding hard seeds. Its sweet-sour flavour is widely used in drinks, sauces and savoury dishes.',
  'uniqueness':'Unlike juicy fruits eaten in segments, tamarind is often valued for the pulp inside a brittle pod. The pulp is used as a souring ingredient across South Asian, African and Latin American cuisines.',
  'flavor':'Pulp can be sharply sour when less mature and increasingly sweet-sour as it matures; cultivar and processing affect flavour.',
  'texture':'The edible pulp is sticky and paste-like, with hard seeds and fibrous strands to remove.',
  'colour':'Pods mature from green to brown; pulp is usually brown and can darken with storage.',
  'season':'Harvest timing depends on tropical and subtropical conditions and often follows a distinct pod-maturation period.',
  'nutrition':'Tamarind pulp contains carbohydrates, fibre and naturally occurring organic acids; processed products can include added sugar or salt.',
  'uses':'Use pulp in chutneys, curries, marinades, soups, drinks and confectionery.',
  'storage':'Intact dry pods keep differently from hydrated pulp. Store prepared pulp in clean, covered containers and follow food-safe refrigeration guidance.',
  'growing':'Tamarind is a long-lived tree suited to warm climates and can tolerate seasonal dryness once established, but young plants need careful establishment.'
 },
 'coconut': {
  'summary':'Coconut is a fibrous drupe whose edible parts include liquid endosperm (coconut water) and firm white endosperm (kernel). Maturity changes the balance between them.',
  'uniqueness':'A coconut has several distinct layers: an outer skin, fibrous husk, hard shell and edible interior. Young and mature coconuts serve different culinary purposes.',
  'flavor':'Young coconut water is mild and refreshing; mature kernel has a richer, nutty flavour.',
  'texture':'Young flesh can be soft and jelly-like, while mature kernel is firm and oily.',
  'colour':'The outer husk varies with cultivar and maturity; the inner kernel is white and the liquid is clear.',
  'season':'In tropical regions, palms may bear throughout the year, though local weather and cultivar influence production.',
  'nutrition':'Coconut water and kernel have different nutrient profiles. Mature kernel contains substantial fat, while the water is mostly liquid.',
  'uses':'Drink coconut water, eat the kernel fresh, grate or dry it, press coconut milk or use it in cooking and baking.',
  'storage':'Once opened, refrigerate coconut water and flesh in clean covered containers. Discard coconut showing rancid smells, mould or unusual deterioration.',
  'growing':'Coconut palms need warmth and space. Coastal adaptation, soil drainage, wind exposure and the time needed to reach bearing age shape cultivation.'
 },
 'persimmon': {
  'summary':'Persimmon fruits range from firm, crisp types to very soft, jelly-like forms. Astringency depends on cultivar and ripeness, so handling advice must match the type.',
  'uniqueness':'Some persimmon cultivars are sweet while still firm; others contain high tannin levels and become pleasant only when fully softened or otherwise properly processed.',
  'flavor':'Flavour can be honeyed, date-like or mild and sweet; tannin-rich types may be strongly astringent before they are ripe.',
  'texture':'Texture ranges from crisp and sliceable to almost spoon-soft.',
  'colour':'Skin and flesh often range from yellow-orange to deep orange-red.',
  'season':'Persimmons are commonly autumn fruits in temperate climates, but season differs by species and growing region.',
  'nutrition':'Persimmon provides fibre and, in orange-fleshed forms, carotenoid pigments; levels vary with cultivar and portion.',
  'uses':'Eat suitable sweet types fresh, soften astringent types fully, or dry and bake fruit in traditional preparations.',
  'storage':'Ripen astringent cultivars to the appropriate stage before eating. Handle ripe fruit gently and refrigerate for short-term storage.',
  'growing':'Choose a species and cultivar suited to winter temperatures and the length of the growing season; some types tolerate colder climates than others.'
 },
 'date': {
  'summary':'Date is the fruit of a palm and is eaten at several maturity stages, from soft fresh dates to semi-dry and dry forms. Cultivars vary in texture, colour and sweetness.',
  'uniqueness':'Date palms produce clusters of fruits that are often harvested in stages. Fresh, soft, semi-dry and fully dry dates may all come from the same cultivar depending on harvest and processing.',
  'flavor':'Dates are naturally sweet, with caramel-like, honeyed, malty or mildly fruity notes depending on cultivar and maturity.',
  'texture':'Fresh dates can be soft and moist; semi-dry and dry forms become chewier and more concentrated.',
  'colour':'Fruit ranges from yellow or amber to red-brown and deep brown at later maturity stages.',
  'season':'Harvest usually follows a seasonal flowering and fruit-development cycle; dates may be sold year-round because many are dried or stored.',
  'nutrition':'Dates are carbohydrate-rich and provide fibre; drying concentrates sugars and energy per weight compared with fresh, higher-moisture fruit.',
  'uses':'Eat as a snack, stuff with fillings, chop into dishes, blend into pastes or use in baking and traditional sweets.',
  'storage':'Store dried dates in a cool, dry, clean container; fresh soft dates generally need cooler storage.',
  'growing':'Date palms are adapted to hot, dry fruit-growing regions, often with irrigation. Pollination and female cultivar choice are important in commercial production.'
 },
 'olive': {
  'summary':'Olive is a small drupe that is central to many Mediterranean food traditions. Fresh fruit is strongly bitter and is typically cured or processed before eating.',
  'uniqueness':'Olives are harvested at different maturity stages and processed to reduce natural bitterness. The same species supplies both table olives and oil, with cultivar traits shaping each use.',
  'flavor':'Depending on cultivar and cure, olives can be grassy, fruity, buttery, briny, peppery or pleasantly bitter.',
  'texture':'Texture may be firm and crisp or softer and more yielding after curing and storage.',
  'colour':'Fruit shifts from green through purple to black as it matures; cured products can have colours that reflect processing as well as maturity.',
  'season':'Harvest timing depends on whether the crop is intended for green table olives, ripe table olives or oil production.',
  'nutrition':'Olives contain fat, much of it oleic acid, as well as salt in many cured preparations. The final nutritional profile depends strongly on processing.',
  'uses':'Cure for table eating, press for olive oil or use in salads, sauces and cooked dishes.',
  'storage':'Follow the storage guidance on cured products; keep brined olives covered by their liquid and use clean utensils.',
  'growing':'Olive trees suit many Mediterranean-type climates, with good drainage and seasonal care. Cold tolerance and oil or table quality vary by cultivar.'
 },
 'quince': {
  'summary':'Quince is a fragrant pome fruit with firm, often astringent flesh when raw. Cooking softens the fruit and can turn its pale flesh pinkish-red.',
  'uniqueness':'Quince has an intense floral aroma and a high pectin content, making it a traditional fruit for jellies, pastes and long-cooked preserves.',
  'flavor':'The raw fruit is tart and astringent; cooking develops a sweet, floral, honey-like flavour.',
  'texture':'Flesh is hard and dense before cooking, then softens gradually and can become translucent.',
  'colour':'The skin is usually yellow when ripe, while cooked flesh can shift from cream to salmon or red.',
  'season':'Harvest often occurs in autumn in temperate regions, with exact timing depending on cultivar and climate.',
  'nutrition':'Quince contributes fibre and naturally occurring pectin; nutrient content depends on the portion and preparation.',
  'uses':'Cook into jelly, quince paste, poached fruit, sauces and baked dishes rather than treating it like a typical raw apple.',
  'storage':'Intact fruit can keep in cool conditions; its strong aroma may transfer to nearby produce.',
  'growing':'Quince grows on a small tree or shrub. Choose varieties adapted to local winters and consider fire-blight and other regional disease pressure.'
 },
 'cacao fruit': {
  'summary':'Cacao grows in ridged pods attached directly to the trunk and older branches. Each pod contains seeds surrounded by sweet-sour pulp; the seeds are processed to make cocoa and chocolate.',
  'uniqueness':'The pod is a large botanical fruit produced by the cacao tree. The familiar chocolate product comes from fermented, dried and roasted seeds rather than the pod’s outer wall.',
  'flavor':'The pulp is fruity and sweet-sour, while the seeds are bitter before fermentation and roasting.',
  'texture':'The pod has a tough rind; individual seeds sit in a soft, mucilaginous pulp.',
  'colour':'Pods can be green, yellow, orange, red or purple depending on cultivar and maturity.',
  'season':'Flowering and pod harvest can occur in flushes in humid tropical climates, with local seasonal peaks.',
  'nutrition':'Cacao pulp and seeds differ markedly in composition. Chocolate products add processing and often sugar, so their nutritional profile is not the same as fresh pulp.',
  'uses':'The pulp can be eaten or fermented into drinks; seeds are fermented, dried and processed into cocoa ingredients.',
  'storage':'Fresh pods should be processed promptly for seed fermentation. Dried cacao beans need protection from moisture and pests.',
  'growing':'Cacao prefers warm, humid conditions, shade when young and well-drained soils; disease management and careful post-harvest fermentation are crucial.'
 },
 'tamarillo': {
  'summary':'Tamarillo, or tree tomato, bears egg-shaped fruits with tangy aromatic flesh. Red and golden forms differ in colour and perceived sweetness.',
  'uniqueness':'Despite the common name, tamarillo is not a tomato cultivar but a distinct plant in the nightshade family. The skin can be bitter, so many preparations scoop or peel the flesh.',
  'flavor':'Flavour is tangy and aromatic, often combining tomato-like savouriness with tart fruit notes.',
  'texture':'The flesh is soft and juicy with many small seeds.',
  'colour':'Red, purple-red, orange and golden forms occur; flesh colour varies within the fruit.',
  'season':'Harvest windows depend on the subtropical climate, plant age and cultivar.',
  'nutrition':'Tamarillo contributes water, fibre and plant pigments; exact composition depends on the colour form and serving.',
  'uses':'Eat the flesh fresh after suitable preparation, or cook into chutneys, sauces, jams and desserts.',
  'storage':'Keep ripe fruit cool and use promptly if the skin is damaged or the flesh has softened substantially.',
  'growing':'Tamarillo is a fast-growing small tree or shrub that prefers mild subtropical conditions and protection from severe frost and wind.'
 },
 'sapodilla': {
  'summary':'Sapodilla is a tropical fruit with brown, grainy flesh and a sweet flavour often compared with brown sugar or malt. Unripe fruit contains latex and is not eaten like fully ripe fruit.',
  'uniqueness':'The fruit is known for its russet-brown skin and sweet, malty flesh. Ripeness is important because immature fruit can be astringent and contain sticky latex.',
  'flavor':'Ripe flesh is mellow and sweet with malt, pear or brown-sugar notes.',
  'texture':'Flesh can be fine-grained or slightly gritty and usually contains several dark seeds.',
  'colour':'Skin is brown and rough; ripe flesh ranges from tan to warm brown.',
  'season':'Warm-region harvest can occur in seasonal flushes, depending on climate and cultivar.',
  'nutrition':'Sapodilla provides carbohydrates and fibre; composition varies by maturity and serving size.',
  'uses':'Eat fully ripe flesh fresh, blend into drinks or use in desserts and preserves.',
  'storage':'Ripen firm fruit at room temperature and refrigerate once ready; avoid eating unripe fruit with abundant latex.',
  'growing':'Sapodilla is adapted to warm tropical and subtropical conditions and may tolerate dry periods once established.'
 },
 'bael': {
  'summary':'Bael is a South Asian tree fruit with a hard outer shell and aromatic pulp. Its use is strongly connected with regional drinks, preserves and traditional food practices.',
  'uniqueness':'The shell is woody and can be difficult to open, while the pulp contains seeds and mucilage. Different maturity stages are used in different regional preparations.',
  'flavor':'Pulp can be fragrant, sweet, tart or resinous depending on maturity and form.',
  'texture':'The interior may be sticky or fibrous, with seeds embedded in the pulp.',
  'colour':'The shell is green to yellow-brown, while pulp colour varies with ripeness and cultivar.',
  'season':'Bael harvest is seasonal in many South Asian regions, with local variation by climate and cultivar.',
  'nutrition':'Bael pulp contains carbohydrates and fibre; composition and preparation vary widely among fresh and processed products.',
  'uses':'Use in drinks, sherbets, preserves and other local preparations after opening and removing unsuitable seeds or fibres.',
  'storage':'The hard shell protects the interior, but any opened pulp should be handled cleanly and stored safely.',
  'growing':'Bael is a hardy tree adapted to tropical and subtropical South Asia; harvest and pulp characteristics vary among local trees.'
 },
 'amla': {
  'summary':'Amla, or Indian gooseberry, is a small ribbed fruit with a strongly sour and astringent taste. It is used fresh in some dishes and widely processed in regional food traditions.',
  'uniqueness':'The pale green fruit has distinctive vertical grooves and a sharp flavour. Amla’s culinary role often involves salting, cooking, drying or preserving to balance its astringency.',
  'flavor':'The taste is sharply sour and astringent, with a lingering finish.',
  'texture':'Flesh is crisp and fibrous around a hard central stone.',
  'colour':'The fruit is usually pale green to yellow-green with faint translucent ribs.',
  'season':'Harvest is generally seasonal in South Asia, though exact months depend on region and cultivar.',
  'nutrition':'Amla is commonly described as a vitamin-C-rich fruit, but amounts vary with variety, maturity, storage and preparation.',
  'uses':'Use in pickles, chutneys, preserves, dried preparations and other traditional foods.',
  'storage':'Keep sound fruit cool and process surplus in a clean, appropriate method for the recipe.',
  'growing':'Amla trees tolerate heat and a range of soils, but establishment, drainage and cultivar choice still affect crop performance.'
 },
 'jamun': {
  'summary':'Jamun, also known as Java plum or jambolan, is a tropical fruit that darkens from green or pink to deep purple as it matures. Its taste balances sweetness with a characteristic astringency.',
  'uniqueness':'The dark-purple skin and staining juice make jamun easy to recognise when ripe. It has a long history in South Asian food cultures and is often eaten fresh during its short season.',
  'flavor':'Sweet, tangy and mildly astringent, with a distinctive fruity finish.',
  'texture':'Juicy flesh surrounds a large seed; the degree of astringency changes with maturity.',
  'colour':'Ripe fruit is usually deep purple to almost black, though colour can vary among trees.',
  'season':'Harvest is seasonal in many South Asian climates and often concentrated into a relatively short window.',
  'nutrition':'Jamun contributes water, fibre and dark plant pigments; nutrient amounts vary by variety and portion.',
  'uses':'Eat fresh, use in drinks and jams, or prepare regional preserves and desserts.',
  'storage':'Fresh fruit bruises easily; keep it cool and use promptly after harvest.',
  'growing':'Jamun trees suit tropical and subtropical conditions and can become large; plan space and harvest access before planting.'
 },
 'passion fruit': {
  'summary':'Passion fruit contains aromatic pulp and many seeds inside a firm rind. Purple and yellow types can differ in acidity, size and growing preferences.',
  'uniqueness':'The edible portion is a fragrant pulp surrounding many seeds. A wrinkled rind often signals ripening for some commonly cultivated types, though cues vary by species and cultivar.',
  'flavor':'The pulp is intensely aromatic, tart-sweet and tropical, with a flavour that remains distinctive even in small amounts.',
  'texture':'Juicy pulp surrounds crunchy edible seeds; the rind is not typically eaten.',
  'colour':'Rinds can be purple, yellow or orange depending on the species and cultivar.',
  'season':'Vines may fruit in flushes or over a long period in warm regions; harvest depends on climate and pollination.',
  'nutrition':'Passion fruit provides fibre in the pulp and seeds, plus water and micronutrients; composition varies among types.',
  'uses':'Scoop the pulp fresh, strain for juice, or use in curds, sauces, desserts and drinks.',
  'storage':'Keep ripe fruit cool. Refrigeration helps maintain quality; cut fruit should be covered and used promptly.',
  'growing':'Passion fruit vines need support, suitable pollination and a climate matched to the species; root health and wind protection matter.'
 },
 'starfruit': {},
}
for s in species:
    fact=FRUIT_FACTS.get(s['name'].lower())
    if fact:
        s.update(fact)

# Actual cultivar names curated as examples from widely documented fruit-growing traditions.
CULTIVARS = {
 'Apple': '''Abbondanza;Abbot's Early;Akane;Alkmene;Allington Pippin;Ambrosia;Anna;Antonovka;Arkansas Black;Ashmead's Kernel;Autumn Glory;Baldwin;Belle de Boskoop;Ben Davis;Braeburn;Bramley's Seedling;Cameo;Candy Crisp;Cortland;Cosmic Crisp;Cox's Orange Pippin;Cripps Pink;Crimson Crisp;Criterion;Discovery;Dorsett Golden;Duchess of Oldenburg;Egremont Russet;Empire;Enterprise;Esopus Spitzenburg;Fuji;Gala;Ginger Gold;Golden Delicious;Golden Russet;Granny Smith;Gravenstein;Honeycrisp;Idared;Jazz;Jonagold;Jonathan;Kanzi;Liberty;Lodi;Lord Lambourne;Macoun;McIntosh;Melrose;Mutsu;Newtown Pippin;Northern Spy;Opal;Orleans Reinette;Orin;Paula Red;Pink Pearl;Pinova;Pristine;Red Delicious;Rhode Island Greening;Ribston Pippin;Rome Beauty;Roxbury Russet;Rubinette;Santana;Sansa;Spartan;Stayman;Summerred;Suncrisp;Sunrise;Sweet Sixteen;Winesap;Wolf River;York Imperial;Zestar!;Ariane;Braeburn Hillwell;Crimson Snow;Elstar;EverCrisp;Fuji Kiku;Glockenapfel;Holsteiner Cox;Ingrid Marie;James Grieve;Karmijn de Sonnaville;Kidd's Orange Red;Laxton's Superb;Lord Derby;Mairac;Morgenduft;Mutsu Crispin;Reinette du Canada;Santana;Topaz;Winter Banana;Worcester Pearmain'''.split(';'),
 'Mango': '''Alphonso;Amrapali;Ataulfo;Banganapalli;Badami;Banganapalle;Bari;Bombay Green;Carabao;Carrie;Chaunsa;Chok Anan;Cogshall;Dasheri;Edward;Fairchild;Fazli;Francis;Glenn;Gomera;Haden;Harumanis;Irwin;Julie;Kesar;Keitt;Kent;Langra;Mallika;Manila;Maya;Mulgoba;Nam Dok Mai;Neelum;Okrung;Palmer;Pickering;Pirie;Rapoza;Raspuri;Red Bush;Rosigold;Royal Special;Sindhri;Southern Blush;Springfels;Tommy Atkins;Valencia Pride;Van Dyke;Zill;P-22;Sweet Tart;Lemon Zest;Orange Sherbet;Ice Cream;Mahachanok;Maha Chanok;Honey Gold;Kensington Pride;Calypso;Honey Kiss;Miyazaki;Totapuri;Pairi;Himsagar;Lakshmanbhog;Fazli;Gulab Khas;Langra Benarsi;Surkha;Chausa;Safeda;Suvarnarekha;Rumani;Neelam;Bangalora;Sindhu;Arka Anmol;Arka Puneet'''.split(';'),
 'Banana': '''Cavendish;Gros Michel;Lady Finger;Manzano;Blue Java;Red Dacca;Pisang Awak;Saba;Cardaba;Nendran;Poovan;Rasthali;Robusta;Ney Poovan;Monthan;Karpuravalli;Pisang Raja;Lakatan;Latundan;Prata;Apple Banana;Burro;Orinoco;Goldfinger;Namwa;Dwarf Cavendish;Williams;Grand Nain;Mysore;Fehi;Yangambi Km5'''.split(';'),
 'Pear': '''Bartlett;Bosc;Comice;Conference;Concorde;D'Anjou;Forelle;Seckel;Starkrimson;Williams;Packham's Triumph;Abate Fetel;Beurré Hardy;Clapp's Favourite;Kieffer;Le Conte;Moonglow;Magness;Passe Crassane;Pyrus Nijisseiki;Shinseiki;Hosui;Kosui;Shinko;Ya Li;Tsu Li;Chojuro;Niitaka;Olympic;20th Century'''.split(';'),
 'Peach': '''Redhaven;Elberta;O'Henry;Reliance;Contender;Cresthaven;Redskin;Belle of Georgia;Donut;Saturn;Flamin' Fury;June Gold;Harvester;Suncrest;Veteran;Madison;Hale Haven;Glohaven;Red Globe;Frost;Ranger;Peregrine;Amsden;Indian Blood;J.H. Hale;July Elberta;Early Redhaven;Loring;Babcock;Pallas'''.split(';'),
 'Nectarine': '''Fantasia;Arctic Star;Arctic Rose;Arctic Jay;Independence;Sunraycer;Flavortop;Snow Queen;Nectared 4;Nectared 6;Harko;Red Gold;Ruby Diamond;May Grand;Firebrite;Stark Red Gold;Silver Lode;Honey Royale;Arctic Glo;September Red'''.split(';'),
 'Plum': '''Santa Rosa;Satsuma;Methley;Beauty;Shiro;Damson;Green Gage;Mirabelle de Nancy;Victoria;President;Stanley;Italian Prune;French Prune;Elephant Heart;Black Amber;Friar;Mariposa;Ozark Premier;Burbank;Laroda;Dapple Dandy;Flavor King;Flavor Queen;Flavor Supreme;Hollywood;Toka;Waneta;Early Laxton;Czar;Opal'''.split(';'),
 'Sweet cherry': '''Bing;Rainier;Lapins;Stella;Van;Chelan;Sweetheart;Skeena;Kordia;Regina;Summit;Black Tartarian;Lambert;Royal Ann;Napoleon;Tieton;Brooks;Benton;Rainier White;Index;Sam;Kristin;Hudson;Attika;Sylvia'''.split(';'),
 'Strawberry': '''Albion;Aromas;Camarosa;Chandler;Elsanta;Festival;Fortuna;Honeoye;Mara des Bois;Monterey;Seascape;Sonata;Sweet Charlie;Albion;Evie-2;Florence;Korona;Malwina;Polka;Senga Sengana;Sparkle;Tribute;Tristar;Earliglow;Jewel;Allstar;Darselect;Diamante;San Andreas;Malling Centenary'''.split(';'),
 'Blueberry': '''Duke;Bluecrop;Legacy;Chandler;Elliott;Aurora;Draper;Liberty;Reka;Spartan;Patriot;Northland;Northblue;Sunshine Blue;Pink Lemonade;Brigitta;Toro;Jersey;Bonus;O'Neal;Misty;Sharpblue;Biloxi;Star;Emerald;Jewel;Sweetcrisp;Powderblue;Tifblue;Climax'''.split(';'),
 'Grape': '''Cabernet Sauvignon;Merlot;Pinot Noir;Chardonnay;Sauvignon Blanc;Riesling;Syrah;Shiraz;Tempranillo;Grenache;Sangiovese;Nebbiolo;Malbec;Carmenère;Zinfandel;Primitivo;Viognier;Gewürztraminer;Muscat Blanc;Concord;Niagara;Thompson Seedless;Flame Seedless;Crimson Seedless;Autumn Royal;Cotton Candy;Moon Drops;Sultana;Kyoho;Shine Muscat;Black Corinth;Ruby Roman;Italia;Cardinal;Red Globe;Perlette;Marquis;Canadice;Reliance;Mars;Jupiter;Muscat of Alexandria'''.split(';'),
 'Orange': '''Valencia;Navel;Washington Navel;Cara Cara;Blood Orange;Moro;Tarocco;Sanguinello;Hamlin;Pineapple Orange;Jaffa;Salustiana;Midknight Valencia;Lane Late;Navelina;Bergamot;Seville Orange;Parson Brown;Ambersweet;Temple;Queen;Maltese Blood;Vaniglia Sanguigno'''.split(';'),
 'Mandarin': '''Ponkan;Dancy;Kinnow;Murcott;Tango;W. Murcott;Page;Minneola;Orri;Dekopon;Shiranui;Satsuma;Owari;Okitsu;Kara;Encore;Fortune;Nova;Sunburst;Fremont;Clementine;Clemenules;Nadorcott;Afourer;Pixie;Fairchild'''.split(';'),
 'Lemon': '''Eureka;Lisbon;Meyer;Femminello;Primofiori;Verna;Interdonato;Villafranca;Ponderosa;Improved Meyer;Monachello;Bearss;Genoa;Lunario;Variegated Pink;Yen Ben'''.split(';'),
 'Lime': '''Key Lime;Persian Lime;Tahiti;Bearss;Kagzi Lime;Rangpur Lime;Mexican Lime;Giant Key Lime;Palestine Sweet Lime;Kusaie Lime;Lakeland Lime;Taneepak'''.split(';'),
 'Avocado': '''Hass;Fuerte;Bacon;Zutano;Pinkerton;Reed;Lamb Hass;Gwen;Gem;Brogden;Choquette;Monroe;Sharwil;Nabal;Ettinger;Maluma;Carmen Hass;Sir Prize;Wurtz;Hellen;Puebla;Mexicola;Duke;Holiday;Lila;Daily 11'''.split(';'),
 'Guava': '''Allahabad Safeda;Lalit;Shweta;Sardar;Lucknow 49;Arka Mridula;Arka Kiran;Arka Amulya;Pant Prabhat;Hisar Safeda;Apple Guava;Ruby Supreme;Red Malaysian;Crystal;Thai Maroon;Tropical Pink;Beaumont;Supreme;Peru;Yellow Cherry'''.split(';'),
 'Papaya': '''Solo;Sunrise Solo;Sunset;Kapoho;Waimanalo;Red Lady;Pusa Delicious;Pusa Nanha;Pusa Majesty;CO-2;CO-7;Arka Surya;Arka Prabhath;Taiwan 786;Tainung 1;Tainung 2;Maradol;Golden;Hawaiian Solo;Eksotika'''.split(';'),
 'Pineapple': '''Smooth Cayenne;Queen;MD-2;Sugarloaf;Red Spanish;Pernambuco;Abacaxi;Kew;Mauritius;Amritha;Gandul;Josapine;N36;Singapore Spanish;Natal Queen;Ripley Queen;Giant Kew;Queen Victoria'''.split(';'),
 'Watermelon': '''Crimson Sweet;Sugar Baby;Charleston Gray;Jubilee;Moon and Stars;Blacktail Mountain;Yellow Crimson;Orangeglo;Allsweet;Dixie Queen;Golden Midget;Mickylee;Tendergold;Charleston Gray;Royal Sweet;Sangria;Seedless 820;Mountain Sweet Yellow;Desert King;Early Moonbeam'''.split(';'),
 'Cantaloupe': '''Hale's Best Jumbo;Hearts of Gold;Ambrosia;Athena;Charentais;Ananas;Galia;Diplomat;Earl's Favourite;Jenny Lind;Minnesota Midget;Sugar Cube;Tuscany;Savor;Hami;Sharlyn;Ogen;Noir des Carmes'''.split(';'),
 'Fig': '''Brown Turkey;Black Mission;Kadota;Celeste;Adriatic;Calimyrna;Desert King;Chicago Hardy;Violette de Bordeaux;Panachée;LSU Purple;LSU Gold;Conadria;White Marseilles;Brunswick;Rouge de Bordeaux;Hardy Chicago;Olympian;Excel;Peter's Honey'''.split(';'),
 'Pomegranate': '''Wonderful;Angel Red;Eversweet;Parfianka;Salavatski;Ambrosia;Desertnyi;Kandahar;Afganski;Mollar de Elche;Haku Botan;Nana;Pink Satin;Sweet;Grenada;Utah Sweet;Sharp Velvet;Purple Heart;Wonderful One;Red Silk'''.split(';'),
 'Persimmon': '''Fuyu;Hachiya;Jiro;Izu;Rojo Brillante;Sharon;Chocolate;Maru;Saijo;Hana Fuyu;Gosho;Suruga;Nishimura Wase;Tamopan;Giombo;Prok;Great Wall;Russian Beauty;Nikitskaia Bordova'''.split(';'),
 'Date': '''Medjool;Deglet Noor;Khadrawy;Barhi;Zahidi;Halawi;Ajwa;Sukkari;Safawi;Mabroom;Khalas;Thoory;Dayri;Iteema;Kenta;Mazafati;Piarom;Rabbi;Sayer;Khenaizi'''.split(';'),
 'Passion fruit': '''Frederick;Possum Purple;Panama Red;Panama Gold;Sweetheart;Nellie Kelly;Misty Gem;Purple Possum;Flavicarpa Yellow;Granadilla;Purple Giant;E-23;BRS Sol do Cerrado;BRS Gigante Amarelo;BRS Ouro Vermelho'''.split(';'),
 'Lychee': '''Mauritius;Brewster;Sweet Cliff;Kwai Mai Pink;No Mai Tsze;Emperor;Hak Ip;Wai Chee;Bengal;Brewster;Kaimana;Bosworth 3;Souey Tung;Haak Yip;Tai So'''.split(';'),
 'Longan': '''Kohala;Biew Kiew;Diamond River;Edau;Chompoo;Ping Pong;Sri Chompoo;Daw;Haew;Itoh;Mekong;Mao Shan Wang'''.split(';'),
 'Jackfruit': '''Black Gold;Dang Rasimi;Golden Nugget;J-31;J-33;Cheena;NS1;Lemon Gold;Varikka;Koozha;Singapore;Tabouey;Kun Wi Chan;Hong Kong;Cochin'''.split(';'),
 'Dragon fruit': '''American Beauty;Vietnamese White;Physical Graffiti;Purple Haze;Delight;Lisa;Makisupa;Sugar Dragon;Voodoo Child;Frankie's Red;Halley's Comet;Yellow Dragon;Natural Mystic;Dark Star;Connie Mayer;Thomson G2'''.split(';'),
 'Coconut': '''Malayan Yellow Dwarf;Malayan Red Dwarf;King Coconut;Chowghat Orange Dwarf;West Coast Tall;East Coast Tall;Maypan;Golden Malayan Dwarf;Green Dwarf;Tiptur Tall;Gangabondam;Kerasree;Kalpa Sree;Kalpa Raksha'''.split(';'),
 'Olive': '''Arbequina;Arbosana;Koroneiki;Picual;Hojiblanca;Frantoio;Leccino;Manzanilla;Kalamata;Picholine;Nocellara del Belice;Gordal;Pendolino;Taggiasca;Mission;Ascolana Tenera;Itrana;Chemlali'''.split(';'),
 'Clementine': '''Clemenules;Nules;Fina;Marisol;Oroval;Oronules;Arrufatina;Hernandina;Algerian;Corsica 2;Corsica 7'''.split(';'),
 'Kiwifruit': '''Hayward;Bruno;Abbott;Monty;Allison;Soreli;Jintao;Zesy002;Zespri SunGold;Zespri Green;Tomua;Jenny'''.split(';'),
 'Apricot': '''Moorpark;Tilton;Goldcot;Harcot;Harglow;Perfection;Blenheim;Royal;Chinese;Katy;Tomcot;Patterson;Robada;Apache;Harlayne;Riland;Puget Gold;Early Golden'''.split(';'),
 'Quince': '''Champion;Pineapple;Smyrna;Aromatnaya;Portugal;Van Deman;Orange;Vranja;Angers;Bereczki'''.split(';'),
 'Blueberry': '''Northcountry;Northsky;Polaris;Chippewa;Duke;Bluecrop;Legacy;Chandler;Elliott;Aurora'''.split(';'),
}

species_by_name={s['name'].lower():s for s in species}
# Alias map handles cultivar groups that use market names or family names.
PARENT_ALIAS = {'Citrus orange':'Sweet orange','Tangerine':'Mandarin','Kiwifruit':'Kiwifruit','Cantaloupe':'Cantaloupe','Blueberry':'Blueberry','Date':'Date','Passion fruit':'Passion fruit'}

cultivar_records=[]
for parent, names in CULTIVARS.items():
    # Resolve parent fruit to seed data using aliases and close matches.
    target = PARENT_ALIAS.get(parent, parent)
    base = species_by_name.get(target.lower())
    if not base:
        choices=[s for s in species if s['name'].lower()==parent.lower()]
        base=choices[0] if choices else None
    if not base:
        # Some cultivar seed categories deliberately refer to a common-name crop not
        # represented in the exact species list; do not create an orphan record.
        continue
    for v in names:
        if not v.strip(): continue
        name=v.strip()
        slug=slugify(name + ' ' + base['name'])
        if any(x['slug']==slug for x in species+cultivar_records): continue
        cultivar_records.append({
          'slug':slug,'name':name,'scientificName':base['scientificName'],'family':base['family'],'group':base['group'],
          'origin':base['origin'],'recordType':'Named cultivar','parentSlug':base['slug'],'parentName':base['name'],
          'summary':f'{name} is a named cultivar associated with {base["name"].lower()}. A cultivar is a selected plant form maintained through propagation; it is not a separate botanical species.',
          'uniqueness':f'The name {name} identifies a selection within {base["name"].lower()} cultivation. A cultivar’s precise flavour, size, colour, harvest date and performance depend on provenance, local climate and growing practice; the name alone does not guarantee identical results everywhere.',
          'flavor':base['flavor'],'texture':base['texture'],'colour':base['colour'],'season':base['season'],
          'nutrition':base['nutrition'],'uses':base['uses'],'storage':base['storage'],'growing':base['growing'],
          'benefits':base['benefits'],'caution':base['caution'],'wikiTitle':base['wikiTitle'],
          'image':base['image'],'tags':[base['group'],base['name'],'named cultivar']
        })

CONCEPTS = {
 'Pomes & temperate fruits': [
  ('Early-season selections','early harvest','Early fruit may be picked before the main harvest peak; flavour and storage quality need to be judged at the cultivar’s proper maturity.'),
  ('Late-season selections','late harvest','Late-season fruit can extend availability into cooler weather, though frost, rain and storage conditions affect the harvest.'),
  ('Long-storage forms','storage','Storage-oriented selections are assessed for firmness, skin condition, disease resistance and how well quality holds after harvest.'),
  ('Fresh-eating forms','dessert','Fresh-eating fruit is commonly valued for a balanced mix of sweetness, acidity, aroma and eating texture.'),
  ('Cooking and preserving forms','culinary','Cooking forms are judged by how well flesh holds its shape, softens evenly, releases juice and balances sugar with acidity.'),
  ('Russeted and textured skins','skin','Skin texture can range from glossy to russeted; appearance alone does not determine eating quality.'),
  ('Red-fleshed forms','flesh colour','Red, pink or deeply pigmented flesh occurs in selected forms of some fruit groups; colour intensity varies with genetics and growing conditions.'),
  ('Cold-climate selections','climate','Cold-climate suitability depends on winter hardiness, chill requirements, bloom timing and the risk of late frost.'),
  ('Traditional landraces','landrace','Traditional landraces are regionally maintained populations or selections whose names and traits can differ between local growing communities.'),
  ('Pollination and seed forms','pollination','Fruit set can depend on flower biology, compatible pollen, pollinators and whether a selection is self-fertile or requires a partner.'),
 ],
 'Stone fruits': [
  ('Early-season selections','early harvest','Early harvest fruit can be especially vulnerable to cool weather and uneven ripening; timing depends on local bloom and cultivar.'),
  ('Late-season selections','late harvest','Late-season selections can extend the picking window, but rain, disease pressure and autumn cooling may affect quality.'),
  ('Freestone forms','pit separation','In freestone types, ripe flesh tends to separate more readily from the pit, which can simplify slicing and processing.'),
  ('Clingstone forms','pit attachment','Clingstone flesh remains more firmly attached to the pit and is often associated with particular processing and eating uses.'),
  ('White-fleshed forms','flesh colour','White-fleshed forms can have delicate aromas and lower visual colour contrast; flavour still depends on ripeness and genetics.'),
  ('Yellow-fleshed forms','flesh colour','Yellow flesh often reflects carotenoid pigments; the shade is not a reliable standalone measure of sweetness.'),
  ('Cold-climate selections','climate','Dormancy needs, flower timing and late-frost exposure are central when matching stone-fruit cultivars to a climate.'),
  ('Drying and preserving forms','preservation','Some fruit types are valued for drying or preserving because their flesh, sugar-acid balance and harvest behaviour suit processing.'),
 ],
 'Citrus fruits': [
  ('Sweet-eating forms','sweetness','Sweet citrus selections balance soluble sugars with acidity; perceived sweetness also depends on maturity and temperature.'),
  ('High-acidity forms','acidity','Acid citrus is often used as a seasoning, juice or preserving ingredient rather than eaten as a whole fruit.'),
  ('Seedless selections','seedlessness','Seedlessness can arise from cultivar genetics and fruit development; performance may change with pollen exposure and environment.'),
  ('Pigmented-flesh forms','pigment','Some citrus types develop pink, red or deep orange flesh pigments; colour intensity can change with climate and maturity.'),
  ('Aromatic-peel forms','peel oils','Citrus peel carries fragrant oils and can contribute intense aroma to cooking, confectionery and beverages.'),
  ('Cold-tolerant selections','climate','Citrus cold tolerance differs greatly by species and cultivar; protected sites and rootstock choice can change outcomes.'),
  ('Mandarin-type forms','peelability','Many mandarin types are selected for easy peeling and segment separation, though rind thickness and texture differ.'),
  ('Juice and processing forms','processing','Processing selections are assessed for juice yield, acidity, colour, aroma and post-harvest handling.'),
 ],
 'Berries & small fruits': [
  ('Early-season selections','early harvest','Early selections start picking sooner in suitable climates, but harvest dates shift with winter chill, spring temperatures and site.'),
  ('Late-season selections','late harvest','Late fruiting forms can extend fresh harvest, although heat, rain and shorter day length may affect yield and flavour.'),
  ('Everbearing and repeat-fruiting forms','fruiting habit','Repeat-fruiting types may produce several flushes rather than one concentrated crop, depending on species and day length.'),
  ('Thornless or easy-picking forms','harvest handling','Plant architecture and thorn presence can influence harvest speed and access, particularly in brambles.'),
  ('Dark-coloured forms','pigment','Dark skins and flesh can contain anthocyanin pigments; colour alone does not establish a health effect or nutrient quantity.'),
  ('Wild and woodland relatives','wild relatives','Wild relatives preserve genetic variation and support wildlife, but safe identification and sustainable harvest are essential.'),
  ('Freezing and preserving forms','preservation','Fruits with balanced acidity, flavour and structure can work well frozen, dried or preserved; texture usually changes after freezing.'),
  ('Container-growing selections','garden growing','Compact growth and manageable root systems can make some selections more suitable for containers, with careful watering and feeding.'),
 ],
 'Grapes & vine fruits': [
  ('Seedless forms','seedlessness','Seedless grapes may still contain small traces of seed tissue; cultivar identity and growing conditions shape berry development.'),
  ('Table-grape forms','fresh eating','Table grapes are usually selected for berry size, texture, flavour, bunch appearance and shelf life.'),
  ('Wine and fermentation forms','fermentation','Wine grapes are assessed for sugar-acid balance, skin chemistry, aroma, tannins and how the berries respond during fermentation.'),
  ('Dark-skinned forms','skin colour','Dark-skinned grapes contain skin pigments; extraction into juice or wine depends on processing as well as cultivar.'),
  ('Muscat-aromatic forms','aroma','Muscat-type grapes are known for pronounced floral and fruity aromas associated with their aromatic compounds.'),
  ('Cool-climate selections','climate','Cool-climate vineyards match varieties to a shorter season, winter lows, disease pressure and the timing of ripening.'),
  ('Drying and raisin forms','drying','Raisin selections are valued for sugar accumulation, berry size, skin behaviour and ease of drying.'),
  ('Disease-resilient forms','resilience','Disease-resilient selections can reduce some management pressures, but site monitoring and integrated crop care remain important.'),
 ],
 'Melons & gourds': [
  ('Early-season forms','early harvest','Early harvest can help in shorter warm seasons, but pollination, warmth and maturity still determine flavour.'),
  ('Orange-fleshed forms','flesh colour','Orange flesh often reflects carotenoid pigments; aroma and ripeness remain important quality cues.'),
  ('Green-fleshed forms','flesh colour','Green-fleshed melons vary in aroma and sweetness; rind pattern and firmness can help assess maturity within a known cultivar.'),
  ('Aromatic dessert forms','aroma','Aroma is a useful cue for many dessert melons, but not all melon types become strongly fragrant when ripe.'),
  ('Long-keeping forms','storage','Long-keeping melons have particular rind and flesh traits; cut fruit still requires prompt refrigeration.'),
  ('Dryland growing forms','water management','Water stress near harvest can alter size, sweetness and yield. Adaptation varies by species and cultivar, not just by fruit group.'),
  ('Regional landraces','landrace','Regional landraces preserve locally selected traits in fruit shape, rind pattern, aroma and crop timing.'),
  ('Seed and pollination forms','pollination','Flowers, pollinators and weather can affect fruit set; crop-specific knowledge helps distinguish poor pollination from other stresses.'),
 ],
 'Tropical & subtropical fruits': [
  ('Early-season harvest forms','early harvest','Harvest timing shifts with rainfall, temperature, flowering flushes and cultivar; a regional calendar is more useful than a global date.'),
  ('Late-season harvest forms','late harvest','Later harvest may extend supply, but storms, heat and post-harvest transport can affect quality and losses.'),
  ('Low-fibre flesh forms','flesh texture','Fibre perception varies within a species; maturity, cultivar and fruit position can affect the eating texture.'),
  ('Aromatic dessert forms','aroma','Aroma can be a key ripeness cue, but the strength and character of scent are species-specific.'),
  ('Green-skinned forms','skin colour','Green peel can remain normal at maturity for many fruits, so colour must be interpreted alongside scent, softness and days after flowering.'),
  ('Red- or purple-skinned forms','skin colour','Red or purple tones may develop through pigment accumulation; sun exposure and temperature can influence colour expression.'),
  ('Yellow- or orange-fleshed forms','flesh colour','Yellow and orange flesh can indicate carotenoid pigments, but the nutritional profile depends on species and serving size.'),
  ('Seed and seedless forms','seed traits','Seed presence, size and germination behaviour vary across species and cultivars; some fruits are usually propagated vegetatively.'),
  ('Drying and preservation forms','preservation','Drying or preserving can extend availability and concentrate flavour, while changing moisture, texture and nutrient levels.'),
  ('Smallholder and home-garden forms','growing context','Home-garden selections may prioritise reliable bearing, manageable size, local taste preferences and resilience to local conditions.'),
  ('Highland and cool-site forms','climate','Elevation changes temperature and growing season; only some tropical fruits tolerate cool nights or cooler highland conditions.'),
  ('Wild relatives and landraces','wild relatives','Wild relatives and landraces can preserve genetic diversity and locally meaningful traits. Names and traits need regional verification.'),
 ],
 'Pomes & temperate fruits': [
  ('Early-season selections','early harvest','Early fruit may be picked before the main harvest peak; flavour and storage quality need to be judged at the cultivar’s proper maturity.'),
  ('Late-season selections','late harvest','Late-season fruit can extend availability into cooler weather, though frost, rain and storage conditions affect the harvest.'),
  ('Long-storage forms','storage','Storage-oriented selections are assessed for firmness, skin condition, disease resistance and how well quality holds after harvest.'),
  ('Fresh-eating forms','dessert','Fresh-eating fruit is commonly valued for a balanced mix of sweetness, acidity, aroma and eating texture.'),
  ('Cooking and preserving forms','culinary','Cooking forms are judged by how well flesh holds its shape, softens evenly, releases juice and balances sugar with acidity.'),
  ('Traditional landraces','landrace','Traditional landraces are regionally maintained populations or selections whose names and traits can differ between local growing communities.'),
  ('Pollination and seed forms','pollination','Fruit set can depend on flower biology, compatible pollen, pollinators and whether a selection is self-fertile or requires a partner.'),
  ('Cold-climate selections','climate','Cold-climate suitability depends on winter hardiness, chill requirements, bloom timing and the risk of late frost.'),
 ],
 'Cacti & dryland fruits': [
  ('Thornless handling forms','harvest handling','Harvest and cleaning require particular care because fine spines or glochids can cling to the surface of some cactus fruits.'),
  ('Deep-coloured flesh forms','flesh colour','Flesh colour varies widely and may reflect natural pigments; colour alone is not a measurement of nutrient content.'),
  ('Sweet dessert forms','fresh eating','Dessert forms are usually judged when fully ripe for sweetness, juiciness and the balance between flesh and seeds.'),
  ('Drought-adapted species profiles','climate','Many dryland plants conserve water, but cultivation still depends on species-specific soil drainage, establishment and seasonal moisture.'),
  ('Seed-rich flesh forms','seed traits','Seeds can dominate texture in some fruits; preparation methods vary by local culinary tradition.'),
  ('Fresh and preserved uses','preservation','Fresh pulp can often be chilled or blended; processing can improve convenience but may change texture and nutrient content.'),
  ('Wild relatives and landraces','wild relatives','Wild desert fruit plants can be culturally important and ecologically adapted; safe identification is essential.'),
  ('Garden and container forms','garden growing','Container cultivation requires free-draining media, sunlight and careful moisture management suited to the plant.'),
 ],
 'Wild & woodland fruits': [
  ('Traditional gathering forms','foraging','Wild fruit gathering should begin with certain identification from a trusted regional guide; common names alone are not enough.'),
  ('Wildlife food profiles','ecology','Fruits can be important seasonal food for birds and mammals, and removing large amounts can reduce resources for wildlife.'),
  ('Tart and astringent forms','flavour','Tartness and astringency vary with species and maturity; some fruits become more palatable after frost, cooking or other traditional processing.'),
  ('Woodland-edge selections','habitat','Woodland-edge conditions often bring changing light, soil moisture and competition, which influence fruiting and plant health.'),
  ('Regional landraces','landrace','Regional forms may preserve local names and uses, though a name can refer to different species in different areas.'),
  ('Preserving and drying forms','preservation','Cooking, drying and preserving are common ways to use seasonal wild fruits; preparation requirements are species-specific.'),
  ('Pollinator and seed ecology','ecology','Flowering, pollination and seed dispersal connect wild fruits to insects, birds, mammals and wider habitat processes.'),
  ('Responsible harvesting','sustainability','Sustainable harvest respects protected species, private land, local rules, wildlife needs and the plant’s ability to regenerate.'),
 ],
 'Pomegranates & figs': [
  ('Early and late harvest forms','harvest','Harvest windows vary by climate and cultivar; ripeness cues include expected colour, texture and sound or feel where locally established.'),
  ('Deep-coloured flesh forms','pigment','Flesh and aril colour can range from pale to deep red; the shade is not a direct measure of sweetness.'),
  ('Sweet-eating selections','fresh eating','Fresh-eating forms balance sweetness, acidity, aroma and texture; seed hardness can strongly influence preference.'),
  ('Drying and preserving forms','preservation','Dried fruit concentrates flavour and sugars as water is removed; storage should limit moisture and pests.'),
  ('Long-keeping forms','storage','Intact fruit may keep much longer than cut fruit. Avoid damaged skins and follow cool, dry storage guidance for the species.'),
  ('Traditional landraces','landrace','Regional fig and pomegranate forms reflect long histories of selection, local climate and cultural food use.'),
  ('Seed and aril texture forms','texture','Seed or aril texture differs among species and cultivars, shaping how fruit is eaten and prepared.'),
  ('Warm-climate growing forms','climate','Sun exposure, heat, water management and winter conditions influence fruit set and quality.'),
 ],
 'Palm & arid-region fruits': [
  ('Fresh harvest forms','harvest','Palm fruit may be harvested at different maturity stages depending on whether the goal is fresh flesh, sap, processing or seed.'),
  ('Dried fruit forms','drying','Drying changes texture and concentrates sugars; safe drying, moisture control and clean storage are essential.'),
  ('Starchy and cooking forms','culinary','Some palm fruits are commonly cooked or processed rather than eaten raw; local food traditions explain the safe preparation method.'),
  ('Arid-land resilience profiles','climate','Many palms are adapted to heat or seasonal dryness, yet establishment and fruiting still depend on species and water access.'),
  ('Coastal and island forms','habitat','Coastal palms can be important parts of island food systems and may tolerate conditions that exclude other crops.'),
  ('Seed and fibre forms','structure','The fruit structure may include thick fibre, hard seed coverings or fleshy outer layers; only the customary edible portion should be used.'),
  ('Traditional processing forms','preservation','Fermentation, syrup-making, drying and cooking can be central to how palm fruits are used and stored.'),
  ('Home-garden and farm forms','growing','Palm spacing, pollination, harvest height and long juvenile periods affect how practical a species is for a home garden or farm.'),
 ],
 'Botanical fruits & unusual edibles': [
  ('Botanical structure profiles','botany','Botanical fruit types develop from flowering plants and differ in how their seeds and surrounding tissues mature.'),
  ('Culinary vegetable uses','culinary','Several fruits are used as savoury vegetables because harvest stage, texture and flavour suit cooked dishes.'),
  ('Seed and pod forms','seed traits','Pods, capsules and berries carry seeds in different structures; the edible part should be confirmed for each species.'),
  ('Cooking and processing forms','processing','Heating, drying, fermenting or removing seeds may be necessary for familiar culinary uses; species-specific guidance matters.'),
  ('Regional food traditions','food culture','Local use names and preparation methods often explain why botanical fruits are eaten differently from sweet dessert fruits.'),
  ('Wild relatives and landraces','wild relatives','Related wild plants can look similar but differ in edibility, so identification should never rely on appearance alone.'),
  ('Harvest-stage profiles','maturity','Some fruit vegetables are harvested immature; changing size, seed development and texture are useful maturity indicators.'),
  ('Storage and handling profiles','storage','The best storage temperature depends on the plant and harvest stage; chilling can damage some tropical produce.'),
 ],
 'Grapes & vine fruits': [
  ('Seedless forms','seedlessness','Seedless grapes may still contain small traces of seed tissue; cultivar identity and growing conditions shape berry development.'),
  ('Table-grape forms','fresh eating','Table grapes are usually selected for berry size, texture, flavour, bunch appearance and shelf life.'),
  ('Wine and fermentation forms','fermentation','Wine grapes are assessed for sugar-acid balance, skin chemistry, aroma, tannins and how berries respond during fermentation.'),
  ('Dark-skinned forms','skin colour','Dark-skinned grapes contain skin pigments; their contribution to juice or wine depends on processing as well as cultivar.'),
  ('Muscat-aromatic forms','aroma','Muscat-type grapes are known for pronounced floral and fruity aromas associated with their aromatic compounds.'),
  ('Cool-climate selections','climate','Cool-climate vineyards match varieties to a shorter season, winter lows, disease pressure and the timing of ripening.'),
  ('Drying and raisin forms','drying','Raisin selections are valued for sugar accumulation, berry size, skin behaviour and ease of drying.'),
  ('Disease-resilient forms','resilience','Disease-resilient selections can reduce some management pressures, but site monitoring and integrated crop care remain important.'),
 ],
}

# Some groups may not have a dedicated map in source data; use the closest sensible
# editorial family map while retaining the base fruit's own group label.
FORM_SOURCE_GROUP = {
 'Citrus fruits':'Citrus fruits','Berries & small fruits':'Berries & small fruits',
 'Grapes & vine fruits':'Grapes & vine fruits','Melons & gourds':'Melons & gourds',
 'Cacti & dryland fruits':'Cacti & dryland fruits','Pomegranates & figs':'Pomegranates & figs',
 'Palm & arid-region fruits':'Palm & arid-region fruits','Wild & woodland fruits':'Wild & woodland fruits',
 'Botanical fruits & unusual edibles':'Botanical fruits & unusual edibles','Stone fruits':'Stone fruits',
 'Pomes & temperate fruits':'Pomes & temperate fruits','Tropical & subtropical fruits':'Tropical & subtropical fruits'
}

def make_form(base, concept, slug_seen):
    title, tag, detail = concept
    name=f'{title} of {base["name"]}'
    slug=slugify(f'{title} {base["name"]} form')
    # same concept+base should be unique, but add stable suffix if common aliases collide
    if slug in slug_seen:
        suffix=hashlib.md5((base['slug']+'|'+title).encode()).hexdigest()[:5]
        slug=f'{slug}-{suffix}'
    slug_seen.add(slug)
    return {
      'slug':slug,'name':name,'scientificName':base['scientificName'],'family':base['family'],'group':base['group'],
      'origin':base['origin'],'recordType':'Fruit-form guide','parentSlug':base['slug'],'parentName':base['name'],
      'summary':f'{name} is an educational guide to a fruit form or selection trait, not a claim that every listed form is a separately registered cultivar. {detail}',
      'uniqueness':f'This profile focuses on {tag} in {base["name"].lower()}. Compare locally documented cultivar descriptions, harvest timing and growing conditions before using a trait to identify or select a plant.',
      'flavor':base['flavor'],'texture':base['texture'],'colour':base['colour'],'season':base['season'],
      'nutrition':base['nutrition'],'uses':base['uses'],'storage':base['storage'],'growing':detail+' '+base['growing'],
      'benefits':base['benefits'],'caution':base['caution'],
      'wikiTitle':base['wikiTitle'],'image':base['image'],'tags':[base['group'],base['name'],tag,'form guide']
    }

# Build catalogue and keep every detail page unique by slug.
all_records=list(species)+list(cultivar_records)
slug_seen={x['slug'] for x in all_records}
form_records=[]
# Use one record per base species per concept. The data label makes clear these are
# educational fruit-form profiles, not fake registered cultivar names.
for base in species:
    concept_group=FORM_SOURCE_GROUP.get(base['group'], 'Tropical & subtropical fruits')
    concepts=CONCEPTS.get(concept_group, CONCEPTS['Tropical & subtropical fruits'])
    # Round-robin a deliberately wide set of concepts. More than one profile per fruit
    # explains distinct growing, harvest, culinary, ecology or structure questions.
    for c in concepts:
        if len(form_records) >= 5000: break
        form_records.append(make_form(base,c,slug_seen))
    if len(form_records)>=5000: break

# Add extra profiles on a second pass if needed; diversify the topic focus for the most
# widely cultivated fruits without implying a formal cultivar registration.
EXTRA_CONCEPTS = [
 ('Regional name and market forms','regional naming','Regional market names can overlap or refer to different plants. Confirm a scientific name when comparing fruit at different markets.'),
 ('Ripeness cues and harvest maturity','ripeness','Ripeness is assessed using species-specific cues such as aroma, softness, days after flowering and the ease of harvest; no single cue works for all fruits.'),
 ('Pest, disease and post-harvest care','post-harvest care','Handling, bruising, temperature and sanitation can affect shelf life. Cultivation and food-safety advice should be adapted to the crop and region.'),
 ('Food culture and traditional uses','food culture','Traditional uses can differ across regions and households; this guide records broad culinary context rather than prescribing a single authentic method.'),
 ('Wild relatives and genetic diversity','genetic diversity','Wild relatives and traditional landraces can preserve valuable diversity, but not every related fruit plant is edible or suitable for cultivation.'),
 ('Small-space and container growing','garden growing','Container growing depends on mature plant size, rootstock or growth habit, light, drainage, climate and whether suitable pollination is possible.'),
 ('Harvest-to-table handling','handling','Clean tools, gentle handling and cool storage can reduce some quality losses. Cut produce should be promptly refrigerated.'),
 ('Seed structure and propagation','propagation','Fruit trees and shrubs may be grown from seed or vegetatively; seed-grown plants can differ from the parent, particularly in named cultivars.'),
]
if len(all_records)+len(form_records)<2600:
    for base in species:
        for c in EXTRA_CONCEPTS:
            if len(all_records)+len(form_records)>=2800: break
            form_records.append(make_form(base,c,slug_seen))
        if len(all_records)+len(form_records)>=2800: break

all_records += form_records
# If seeded species count shifts, trim to 2,800 catalogue pages while preserving all
# species and named cultivar records first.
if len(all_records)>2800:
    all_records = list(species)+list(cultivar_records)+form_records[:max(0,2800-len(species)-len(cultivar_records))]

# IDs and related fruit suggestions make the full dataset convenient to query offline.
slugs_by_group={}
for r in all_records: slugs_by_group.setdefault(r['group'], []).append(r['slug'])
for r in all_records:
    pool=[s for s in slugs_by_group.get(r['group'],[]) if s!=r['slug']]
    digest=hashlib.md5(r['slug'].encode()).hexdigest()
    start=int(digest[:6],16)%max(1,len(pool))
    r['related']=[pool[(start+i*7)%len(pool)] for i in range(min(4,len(pool))) ] if pool else []
    r['searchText']=' '.join([r['name'],r['scientificName'],r['family'],r['group'],r['origin'],r.get('parentName',''),*r['tags']]).lower()
    r['image']=r.get('image') or IMAGE_URLS.get(r['group'],IMAGE_URLS['default'])

# Guide data used by non-catalogue sections.
guides = [
 {'slug':'fruit-botany-from-flower-to-fruit','title':'Fruit botany: from flower to fruit','category':'Botany','readTime':'8 min','intro':'Learn how flowers develop into fruit, why botanical definitions differ from culinary labels, and what the fruit wall tells us about plant evolution.','sections':[{'heading':'What counts as a fruit?','body':'In botany, a fruit develops from the ovary of a flowering plant and usually surrounds seeds. The everyday word fruit is shaped by taste and food culture, so tomatoes, cucumbers, olives and nuts can sit in different culinary categories than botanical ones.'},{'heading':'Fruit structures','body':'Berries, drupes, pomes, pepos, capsules and aggregate fruits develop in different ways. A peach is a drupe with a hard stone; an apple is a pome with much of its edible flesh arising from floral tissues; a strawberry is an aggregate accessory fruit with its tiny achenes on the outside.'},{'heading':'Why structure matters','body':'Structure helps explain seed position, ripening, handling and dispersal. It also helps botanists compare related plants without relying on common names, which may vary from region to region.'}]},
 {'slug':'nutrition-without-the-myths','title':'Fruit nutrition without the myths','category':'Food & nutrition','readTime':'7 min','intro':'Understand fibre, water, vitamins, minerals and plant pigments without treating one fruit as a miracle food.','sections':[{'heading':'A varied pattern matters','body':'Fruits differ greatly in their nutrient composition. Whole fruits commonly contribute water and fibre, and many provide vitamin C, folate, potassium or colourful plant compounds. No single fruit supplies every nutrient in the amounts a person needs.'},{'heading':'Whole fruit and juice','body':'Juice can provide flavour and some micronutrients, but it usually has less intact fibre than whole fruit and is easier to consume quickly. Serving size and preparation matter when comparing foods.'},{'heading':'Be cautious with health claims','body':'A fruit is not a treatment for disease. Nutrition depends on the whole eating pattern, portion, variety, individual tolerance and any relevant medical advice. This encyclopedia avoids unsupported disease-prevention promises.'}]},
 {'slug':'how-to-judge-ripeness','title':'How to judge fruit ripeness','category':'Harvest & storage','readTime':'6 min','intro':'Use species-specific cues—rather than colour alone—to decide when a fruit is ready to pick or eat.','sections':[{'heading':'Colour is only one clue','body':'Some fruits change colour as they mature, while others remain green or develop colour unevenly. Sun exposure can alter the peel without guaranteeing ripe flesh.'},{'heading':'Smell, feel and timing','body':'A characteristic aroma, slight yielding, the ease of separating fruit from the plant, and days since flowering can be useful clues. The right combination depends on the species and cultivar.'},{'heading':'After harvest','body':'Some fruits continue to soften and develop aroma after picking; others must mature on the plant for the best flavour. Follow crop-specific guidance and handle fruit gently to reduce bruising.'}]},
 {'slug':'fruit-storage-and-food-safety','title':'Fruit storage and safe handling','category':'Harvest & storage','readTime':'8 min','intro':'Keep produce fresh longer with clean handling, suitable temperatures and attention to cut-fruit safety.','sections':[{'heading':'Start with gentle handling','body':'Bruises and punctures shorten the useful life of many fruits. Separate damaged pieces from sound produce and keep storage areas clean and ventilated.'},{'heading':'Room temperature or refrigeration?','body':'Some fruits ripen well at room temperature; refrigeration slows deterioration once they are ripe. Certain tropical fruits can be damaged by excessive cold, so storage should be species-specific.'},{'heading':'Cut fruit needs care','body':'Refrigerate cut fruit promptly in clean covered containers. Wash whole fruit under clean running water before cutting, and use clean knives and cutting boards.'}]},
 {'slug':'fruit-seasons-around-the-world','title':'Fruit seasons around the world','category':'Seasonality','readTime':'7 min','intro':'Harvest calendars move with hemispheres, elevation, rainfall, varieties and protected cultivation.','sections':[{'heading':'There is no single global season','body':'A fruit may be in season in one country while coming from cold storage or a different hemisphere elsewhere. Local rainfall cycles and flowering patterns can matter more than calendar months for tropical crops.'},{'heading':'Varieties extend harvest windows','body':'Growers can combine early, mid-season and late selections to spread harvest. Cultivar names do not imply identical dates in every climate.'},{'heading':'Use a local calendar','body':'Treat season charts as regional guides and confirm current availability with local growers and markets. Weather variation can shift the window from year to year.'}]},
 {'slug':'growing-fruit-at-home','title':'Growing fruit at home','category':'Growing','readTime':'9 min','intro':'Choose a fruit for your climate, light, available space and pollination needs before choosing a cultivar.','sections':[{'heading':'Match plant to place','body':'Sunlight, winter chill, summer heat, soil drainage and water availability shape success. A tropical fruit may struggle in a cool temperate garden, while some temperate trees need winter chill.'},{'heading':'Understand pollination','body':'Some cultivars set fruit with their own pollen; others need compatible partners and pollinators. Check this before planting, especially if space is limited.'},{'heading':'Plan for maturity','body':'A fruit tree or vine can take years to reach full production. Consider mature size, pruning, rootstock, disease resistance and how fruit will be harvested.'}]},
 {'slug':'traditional-landraces-and-biodiversity','title':'Traditional landraces and fruit biodiversity','category':'Biodiversity','readTime':'8 min','intro':'Why local fruit forms, wild relatives and seed collections matter for food culture and future growing resilience.','sections':[{'heading':'What is a landrace?','body':'A landrace is a locally maintained population or traditional crop form shaped by selection, environment and cultural use. It may be genetically diverse rather than uniform like a modern commercial cultivar.'},{'heading':'Why names can be complicated','body':'The same name can refer to different fruit forms in different places, and one plant may have several regional names. Scientific names, local references and provenance records help keep identities clear.'},{'heading':'Conservation in practice','body':'Home gardens, community orchards, seed banks, field collections and farmer networks can preserve living diversity. Sustainable wild harvesting also leaves enough fruit for wildlife and regeneration.'}]},
 {'slug':'understanding-cultivar-names','title':'Understanding fruit cultivar names','category':'Field guide','readTime':'6 min','intro':'Learn how species, cultivar names, synonyms and market labels fit together in a fruit catalogue.','sections':[{'heading':'Species versus cultivar','body':'A species is a botanical unit. A cultivar is a selected cultivated plant maintained for particular traits, generally by suitable propagation. Cultivar names do not automatically indicate a separate species.'},{'heading':'Synonyms and trade names','body':'Some selections are known by a regional name, translated name or trademark. Catalogues may group synonyms differently, so look for provenance and reliable horticultural references.'},{'heading':'What this atlas includes','body':'The catalogue distinguishes core species profiles, curated named-cultivar entries and editorial form guides. Form guides explore traits such as ripening, flesh colour or growing context and are not presented as registered cultivar names.'}]},
]

# Export exactly the profile rows present in the final catalogue.
form_records_final = all_records[len(species)+len(cultivar_records):]
(DATA/'base-fruits.json').write_text(json.dumps(species,ensure_ascii=False,indent=2),encoding='utf-8')
(DATA/'named-cultivars.json').write_text(json.dumps(cultivar_records,ensure_ascii=False,indent=2),encoding='utf-8')
(DATA/'fruit-form-profiles.json').write_text(json.dumps(form_records_final,ensure_ascii=False,indent=2),encoding='utf-8')
(DATA/'fruits.json').write_text(json.dumps(all_records,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
# Preserve the expanded educational library when rebuilding the generated fruit catalogue.
# The source below defines the eight starter articles; any additional authored guides are
# retained from data/guides.json, and saved versions of the starter guides remain editable.
existing_guides_path = DATA / 'guides.json'
if existing_guides_path.exists():
    saved_guides = json.loads(existing_guides_path.read_text(encoding='utf-8'))
    saved_by_slug = {guide.get('slug'): guide for guide in saved_guides if guide.get('slug')}
    starter_slugs = {guide['slug'] for guide in guides}
    guides = [saved_by_slug.get(guide['slug'], guide) for guide in guides]
    guides.extend(guide for guide in saved_guides if guide.get('slug') not in starter_slugs)
(DATA/'guides.json').write_text(json.dumps(guides,ensure_ascii=False,indent=2),encoding='utf-8')

# A compact group index for the site; group slugs remain stable across fruit-data changes.
groups=[]
for group in sorted(set(s['group'] for s in species)):
    samples=[s for s in species if s['group']==group]
    groups.append({'slug':slugify(group),'name':group,'count':sum(1 for r in all_records if r['group']==group),'speciesCount':len(samples),'description':GROUP_INFO.get(group,GROUP_INFO['Tropical & subtropical fruits'])[0].capitalize()+'.','image':samples[0]['image'],'examples':[s['name'] for s in samples[:6]]})
(DATA/'groups.json').write_text(json.dumps(groups,ensure_ascii=False,indent=2),encoding='utf-8')

# Small reference glossary with concise, non-medical definitions.
glossary=[
 ('Accessory fruit','A fruit-like structure in which tissues beyond the ovary contribute substantially to the edible part.'),('Aggregate fruit','A fruit structure formed from several separate ovaries of a single flower, as in raspberry.'),('Berry','In botany, a fleshy fruit developing from one ovary, often with seeds embedded in the pulp.'),('Brix','A measure of soluble solids often used as an approximate indicator of sugar content in fruit juice.'),('Chill requirement','The amount of cool winter exposure some temperate plants need for normal bud break and flowering.'),('Climacteric fruit','A fruit that generally shows a rise in respiration during ripening and may continue to ripen after harvest.'),('Cultivar','A cultivated plant selection maintained for consistent traits through appropriate propagation.'),('Drupe','A fruit with fleshy outer tissue and a hard inner layer surrounding the seed, such as a peach.'),('Ethylene','A plant hormone involved in ripening and other developmental processes.'),('Flavedo','The coloured outer part of citrus peel, rich in aromatic oil glands.'),('Landrace','A locally maintained crop population shaped by tradition, selection and environment.'),('Locule','A chamber in an ovary or fruit that may contain seeds.'),('Non-climacteric fruit','A fruit that generally does not show the classic climacteric respiratory rise during ripening.'),('Pepo','A type of berry with a hard rind, typical of cucurbits such as melons.'),('Pome','A fruit type in which accessory floral tissues contribute to the fleshy part, as in apples and pears.'),('Pollination','Transfer of pollen to the receptive part of a flower, enabling fertilisation in many plants.'),('Rootstock','The rooted part of a grafted plant onto which a cultivar is joined.'),('Scion','The upper part of a grafted plant that determines the cultivar identity.'),('Stone','The hard inner layer of a drupe surrounding its seed.'),('Tannin','A class of plant compounds that can contribute astringency in some fruits.'),('Zest','The aromatic coloured outer peel of citrus, used in food in small quantities.')]
(DATA/'glossary.json').write_text(json.dumps([{'slug':slugify(a),'term':a,'definition':b} for a,b in glossary],ensure_ascii=False,indent=2),encoding='utf-8')

counts={
 'catalogueRecords':len(all_records),'speciesProfiles':len(species),'namedCultivars':len(cultivar_records),'fruitFormGuides':len(form_records_final),'groups':len(groups),'guides':len(guides),'glossary':len(glossary)
}
(DATA/'catalogue-stats.json').write_text(json.dumps(counts,indent=2),encoding='utf-8')
print(counts)
print('unique slugs',len({x['slug'] for x in all_records}))
print('size fruits.json', (DATA/'fruits.json').stat().st_size)
