export interface JargonConcept {
  id: number;
  name: string;
  category: 'Basic' | 'Intermediate' | 'Advanced';
  level1: string; // Standard Simplified
  level2: string; // ELI5 Metaphor
  level3: string; // Cartoon Superhero / Game Analogy
}

export interface JargonSet {
  id: string;
  name: string;
  description: string;
  icon: string;
  themeColor: string; // HSL color or CSS class
  bgClass: string;
  concepts: JargonConcept[];
}

export const JARGON_SETS: JargonSet[] = [
  {
    id: 'web-sorcery',
    name: '🌐 Web & Network Sorcery',
    description: 'Learn how the internet works, from browsers to globally scaled cloud architectures.',
    icon: 'Globe',
    themeColor: '#4ECDC4',
    bgClass: 'bg-teal-cartoon',
    concepts: [
      {
        id: 1,
        name: 'Client',
        category: 'Basic',
        level1: 'The device or software (like your web browser) that requests information from a network.',
        level2: 'Like a customer at a restaurant table looking at a menu and placing an order.',
        level3: 'A hungry cartoon squirrel shouting orders into a magic pipe hoping a nut comes out!'
      },
      {
        id: 2,
        name: 'Server',
        category: 'Basic',
        level1: 'A computer or program that stores data and serves requested information back to clients.',
        level2: 'Like the kitchen in a restaurant that takes orders, cooks the food, and sends it out.',
        level3: 'A giant robot butler in a skyscraper who grabs toys from shelves and tosses them down chutes.'
      },
      {
        id: 3,
        name: 'IP Address',
        category: 'Basic',
        level1: 'A unique numerical label assigned to each device connected to a computer network.',
        level2: 'Like your home mailing address so the mailman knows exactly where to deliver letters.',
        level3: 'The coordinates of your secret superhero base so delivery drones can drop off pizza.'
      },
      {
        id: 4,
        name: 'HTTP Request',
        category: 'Basic',
        level1: 'A message sent by a client to a server asking for a web page or resource.',
        level2: 'Like writing a letter to a store asking, "Do you have this toy in stock?"',
        level3: 'A paper airplane thrown at a tower with "GIVE ME THE CAT PICTURES" scribbled in crayon.'
      },
      {
        id: 5,
        name: 'HTTP Response',
        category: 'Basic',
        level1: 'The data returned by a server to a client, including status codes and content.',
        level2: 'Like the store owner sending a package back with your toy or a note saying they are out.',
        level3: 'A balloon dropping from the tower containing a giant scroll of text and a stamp of approval!'
      },
      {
        id: 6,
        name: 'DNS',
        category: 'Basic',
        level1: 'The Domain Name System translates human-friendly URLs into computer IP addresses.',
        level2: 'Like the contacts list on your phone that translates "Mom" into a phone number.',
        level3: 'A wise old owl sitting on a pole who shouts coordinates when you show him a nametag.'
      },
      {
        id: 7,
        name: 'Port',
        category: 'Basic',
        level1: 'A virtual communication endpoint that directs traffic to specific software on a server.',
        level2: 'Like apartment numbers in a building ensuring letters go to the right person.',
        level3: 'Numbered intake pipes on a spaceship: Pipe 80 is for water, Pipe 22 is for astronauts.'
      },
      {
        id: 8,
        name: 'URL',
        category: 'Basic',
        level1: 'Uniform Resource Locator: the full web address used to find a resource on the internet.',
        level2: 'Like a complete set of directions: "Go to Main Street, enter Building A, room 5."',
        level3: 'A magical treasure map scroll that reads: "Kingdom of Google, Castle Search, Vault Images."'
      },
      {
        id: 9,
        name: 'Domain Name',
        category: 'Basic',
        level1: 'The easy-to-remember name of a website, like google.com, pointing to an IP address.',
        level2: 'Like the sign on a storefront showing the store\'s name rather than its GPS coordinate.',
        level3: 'The flag flying above a castle so knights know which kingdom they are entering.'
      },
      {
        id: 10,
        name: 'Socket',
        category: 'Basic',
        level1: 'An open connection link between two nodes on a network for sending data back and forth.',
        level2: 'Like a tin-can telephone with a string stretched tight between two windows.',
        level3: 'A glowing energy tube plugged directly from a robot\'s head into a main control socket.'
      },
      // Generate subsequent nodes in streamlined chunks to cover all 100 concepts
      ...Array.from({ length: 90 }, (_, index) => {
        const id = index + 11;
        const names = [
          'HTML', 'CSS', 'JavaScript', 'DOM', 'Cookie', 'LocalStorage', 'Session', 'API', 'JSON', 'REST API',
          'HTTP Methods', 'Status Codes', 'HTTP Header', 'CORS', 'HTTPS', 'SSL/TLS', 'Certificate Authority', 'Load Balancer', 'Reverse Proxy', 'CDN',
          'Cache', 'TTL', 'WebSockets', 'gRPC', 'Protocol Buffers', 'Message Queue', 'Pub/Sub', 'Webhook', 'Server-Sent Events', 'Single Page App (SPA)',
          'SSR (Server-Side Rendering)', 'SSG (Static Site Generation)', 'Hydration', 'Bundler', 'Transpiler', 'JWT (JSON Web Token)', 'OAuth', 'Session Cookie', 'XSS (Cross-Site Scripting)', 'CSRF',
          'Rate Limiting', 'API Throttling', 'HTTP Keep-Alive', 'Microservices', 'Monolith', 'Serverless', 'Docker Container', 'Kubernetes', 'Service Mesh', 'DNS Anycast',
          'TCP Handshake', 'UDP', 'WebRTC', 'HTTP/2', 'HTTP/3', 'Edge Computing', 'Cold Start', 'CI/CD', 'Zero-Downtime Deployment', 'API Gateway',
          'SQL', 'NoSQL', 'ORM', 'Query Indexing', 'Database Transaction', 'ACID Properties', 'CAP Theorem', 'Sharding', 'Replication', 'Connection Pool',
          'IP Routing', 'Subnet', 'NAT (Network Address Translation)', 'VPN', 'Firewall', 'Web Server', 'App Server', 'Static Assets', 'CSS Grid', 'Flexbox',
          'Responsive Web Design', 'Media Queries', 'Semantic HTML', 'SEO Metadata', 'Browser Engine', 'V8 Engine', 'Event Loop', 'Callback Queue', 'Promise', 'Async/Await'
        ];
        
        const category: 'Basic' | 'Intermediate' | 'Advanced' = 
          id <= 30 ? 'Basic' : id <= 70 ? 'Intermediate' : 'Advanced';
          
        const name = names[index] || `Concept-${id}`;
        
        // Custom level definitions written in structured form:
        const database: Record<string, [string, string, string]> = {
          'HTML': [
            'The structural language of web pages, defining elements like paragraphs, headings, and images.',
            'The wooden skeleton or framing of a house before you paint or furnish it.',
            'A skeleton made of bricks holding cardboard signs that say "TITLE", "TEXT", and "BUTTON".'
          ],
          'CSS': [
            'Style sheets used to describe the presentation and layout of a document written in HTML.',
            'The paint, wallpaper, and decorations that make a house look beautiful and styled.',
            'A magic paintbrush that flies around spraying glitter, coloring walls, and moving furniture.'
          ],
          'JavaScript': [
            'A programming language that allows you to make web pages interactive and dynamic.',
            'The plumbing, light switches, and appliances that make a house actually function.',
            'A hyperactive wizard casting spells on buttons so they dance and scream when touched.'
          ],
          'DOM': [
            'Document Object Model: The structured tree representation of a web page created by the browser.',
            'The blueprint of a house that lets you inspect and modify any room or wall on the fly.',
            'A giant family tree of boxes where you can rename children, move rooms, or chop branches off.'
          ],
          'Cookie': [
            'Small pieces of text data saved in your browser by a website to remember your preferences.',
            'Like a hand-stamp at an amusement park that shows they already checked your ticket.',
            'A crumb left in your pocket by a butler so they recognize you when you knock on the door.'
          ],
          'LocalStorage': [
            'A browser storage system that saves key-value data with no expiration date.',
            'Like a small locker in your bedroom where you can store personal items permanently.',
            'A magic backpack that holds your high scores and game settings even if you close the game.'
          ],
          'Session': [
            'A temporary state of interaction between client and server, cleared when the user leaves.',
            'Like a conversation with a shopkeeper that ends and is forgotten once you walk out the door.',
            'A magic bubble that pops and disappears when you close your browser tab.'
          ],
          'API': [
            'Application Programming Interface: A way for two software systems to communicate and share data.',
            'Like a waiter taking your order to the kitchen and bringing back your meal.',
            'A slot in a castle wall where you slip in a question card and get a scroll back.'
          ],
          'JSON': [
            'JavaScript Object Notation: A lightweight data format for sharing text-based structured data.',
            'Like a standard fill-in-the-blank form where information is written in clean rows.',
            'A cardboard box labeled with sticky notes telling you exactly what toy is inside.'
          ],
          'REST API': [
            'An API style that uses standard HTTP requests to get, put, post, and delete data.',
            'Like a vending machine where you press specific buttons to get standard items.',
            'A castle checkpoint where guards only accept standard request forms with green stamps.'
          ],
          'HTTP Methods': [
            'Verbs like GET, POST, PUT, and DELETE indicating the action a request wants to perform.',
            'Like using action words: "read the book", "create a page", "edit the text", "destroy it".',
            'Colored flags: Green for "Gimme", Yellow for "Add", Blue for "Replace", Red for "Smash!"'
          ],
          'Status Codes': [
            'Three-digit numbers returned by a server indicating if a request was successful or failed.',
            'Like a thumbs up, thumbs down, or a question mark from a librarian.',
            'Signs held up by a referee: 200 (Score!), 404 (Lost ball!), 500 (Ref fainted!).'
          ],
          'HTTP Header': [
            'Extra meta-information sent with HTTP requests/responses, like content-type or auth tokens.',
            'Like the shipping label on a package showing weight, fragile status, and origin.',
            'A hats-on-letters system: a top hat for secret codes, a chef hat for JSON recipes.'
          ],
          'CORS': [
            'Cross-Origin Resource Sharing: A security mechanism that restricts resources loaded from other domains.',
            'Like a security guard at a building entrance checking if you are allowed to invite outsiders.',
            'A protective forcefield that shocks requests coming from unauthorized rival castles.'
          ],
          'HTTPS': [
            'Hypertext Transfer Protocol Secure: Encrypted web traffic ensuring safe data transmission.',
            'Like sending your mail in a locked steel safe instead of an open paper envelope.',
            'An armored truck driving through tunnel passages instead of a paper airplane in the wind.'
          ],
          'SSL/TLS': [
            'Cryptographic protocols that secure communication over a network using encryption keys.',
            'Like the secret lock and key system used to secure the steel safe.',
            'A magical invisibility cloak wrapped around all packets traveling through space.'
          ],
          'Certificate Authority': [
            'An entity that issues digital certificates to verify the true identity of websites.',
            'Like a government office that issues official passports to verify who you are.',
            'A royal council that stamps shields to certify a castle is a real ally, not a bandit hideout.'
          ],
          'Load Balancer': [
            'A device that distributes incoming network traffic across multiple servers to prevent overload.',
            'Like a traffic cop directing cars to different lanes so no single lane jams up.',
            'A cartoon dealer handing cards to a circle of servers as fast as possible.'
          ],
          'Reverse Proxy': [
            'A server that sits in front of backend servers, routing client requests and adding security.',
            'Like a receptionist at an office building who talks to visitors so they don\'t wander inside.',
            'A decoy castle gate where a dummy wizard answers questions on behalf of the real wizard.'
          ],
          'CDN': [
            'Content Delivery Network: Geographically distributed servers caching content closer to users.',
            'Like a grocery store chain placing local stores nearby so you don\'t drive to the farm.',
            'A network of copycats stationed around the globe holding duplicate scrolls for instant delivery.'
          ],
          'Cache': [
            'A temporary storage area that holds frequently requested data for fast access.',
            'Like keeping your favorite book on your desk instead of walking to the basement library.',
            'A pocket where you keep a few pieces of candy so you don\'t have to run to the kitchen.'
          ],
          'TTL': [
            'Time To Live: A value that limits the lifespan of data in a cache or network routing.',
            'Like an expiration date on milk indicating when it should be thrown away.',
            'A self-destruct timer ticking down on a message scroll before it burns to ash.'
          ],
          'WebSockets': [
            'A communication protocol providing full-duplex, real-time channels over a single connection.',
            'Like keeping an open phone line where both people can talk at the same time.',
            'A magical glowing portal that remains open for messages to zip back and forth instantly.'
          ],
          'gRPC': [
            'A high-performance Remote Procedure Call framework developed by Google.',
            'Like a direct intercom connecting two offices to talk in highly optimized codes.',
            'A super-fast pneumatic tube system shooting compressed cylinders between robot brains.'
          ],
          'Protocol Buffers': [
            'A language-neutral, binary format for serializing structured data used in gRPC.',
            'Like packing clothing into a vacuum-sealed bag to make it as tiny as possible.',
            'Squishing standard messages into tiny glowing energy pellets for instant transport.'
          ],
          'Message Queue': [
            'A system that stores messages sequentially until receiving applications process them.',
            'Like a line of people waiting to buy tickets; the agent serves them one by one.',
            'A conveyor belt where messages sit in boxes waiting for robot claws to open them.'
          ],
          'Pub/Sub': [
            'Publisher/Subscriber: A messaging pattern where senders broadcast to topics without knowing receivers.',
            'Like a newspaper agency printing papers for subscribers without knowing who they are.',
            'A radio tower broadcasting music to any cartoon robot tuned into the station.'
          ],
          'Webhook': [
            'An automatic notification sent from one app to another when a specific event occurs.',
            'Like asking a friend, "Text me the second the package arrives" instead of calling them hourly.',
            'A tripwire that triggers a flare gun to shoot at a neighboring castle when a door opens.'
          ],
          'Server-Sent Events': [
            'A technology where a server pushes real-time updates to a client over HTTP.',
            'Like tuning into a live loudspeaker broadcast that keeps feeding you news.',
            'A long scroll rolling out of a wall slot, continuous and never-ending.'
          ],
          'Single Page App (SPA)': [
            'A web application that loads a single document and updates content dynamically without reloading.',
            'Like a book where the text magically morphs on the page instead of turning the page.',
            'A theater stage where backdrops are swapped out instantly while the actors keep running.'
          ],
          'SSR (Server-Side Rendering)': [
            'Generating the full HTML of a page on the server before sending it to the client.',
            'Like ordering a fully assembled LEGO model rather than a box of loose bricks.',
            'A wizard painting a beautiful picture and throwing the completed canvas over the wall.'
          ],
          'SSG (Static Site Generation)': [
            'Pre-rendering web pages into static files at build time before users request them.',
            'Like pre-printing millions of copies of a book and stockpiling them in warehouses.',
            'A printing press cranking out thousands of posters in advance to hand out instantly.'
          ],
          'Hydration': [
            'A process where client-side JavaScript attaches event listeners to server-rendered HTML.',
            'Like putting batteries into a pre-built toy to make it move and light up.',
            'Sprinkling magic water on a paper statue to turn it into a living, dancing companion.'
          ],
          'Bundler': [
            'A tool that combines multiple code files and assets into a single optimized file.',
            'Like packing all your vacation clothes and gear into one compact suitcase.',
            'A trash compactor that squishes thousands of scrolls into one glowing master cube.'
          ],
          'Transpiler': [
            'A tool that translates source code from one language to another similar language.',
            'Like translating a book from Old English to Modern English so it\'s easier to read.',
            'A magic translator bubble that turns advanced futuristic code into old-fashioned scrolls.'
          ],
          'JWT (JSON Web Token)': [
            'A compact URL-safe means of representing claims securely between two parties.',
            'Like a ticket with an official signature that proves you paid and belong inside.',
            'A glowing badge with a digital wax seal that guards read to let you enter.'
          ],
          'OAuth': [
            'An open standard for access delegation, letting users share resources without sharing passwords.',
            'Like giving a hotel valet a temporary key that only starts the car and opens the trunk.',
            'A signed letter from a king granting a knight access to a specific castle kitchen.'
          ],
          'Session Cookie': [
            'A temporary cookie that is deleted when the user closes the web browser.',
            'Like a hand stamp made with erasable ink that washes off when you leave the park.',
            'A melting ice-sculpture badge that dissolves as soon as you step out of the castle.'
          ],
          'XSS (Cross-Site Scripting)': [
            'A security vulnerability where attackers inject malicious scripts into trusted websites.',
            'Like a trickster writing a fake recipe in a chef\'s cookbook that poisons the soup.',
            'A goblin sneaking a mind-control scroll into a wizard\'s delivery pigeon bag.'
          ],
          'CSRF': [
            'Cross-Site Request Forgery: Tricking a user into executing unwanted actions on an authenticated site.',
            'Like a thief forging your signature on a check to buy a car while you are asleep.',
            'A sneaky goblin guide leading a sleepwalking king to sign a decree giving away gold.'
          ],
          'Rate Limiting': [
            'Limiting the number of requests a user can make to a server in a given timeframe.',
            'Like a store only allowing customers to buy two boxes of cereal per day.',
            'A security gate that dumps a bucket of water on anyone who knocks more than 5 times.'
          ],
          'API Throttling': [
            'Slowing down requests from a user when they exceed a rate limit rather than blocking.',
            'Like a traffic cop making cars drive at a slow crawl instead of blocking the road entirely.',
            'A wizard casting a slow-motion spell on a hyperactive delivery pigeon.'
          ],
          'HTTP Keep-Alive': [
            'Using a single TCP connection to send and receive multiple HTTP requests/responses.',
            'Like keeping the phone line active instead of hanging up and redialing after every sentence.',
            'A bridge that stays lowered for all carts rather than raising and lowering for each one.'
          ],
          'Microservices': [
            'An architectural style structuring an application as a collection of small autonomous services.',
            'Like a restaurant run by specialized chefs: one only boils pasta, one only chops sauce.',
            'A fleet of tiny modular ships flying together instead of one giant space cruiser.'
          ],
          'Monolith': [
            'A software application where all components are combined into a single, unified codebase.',
            'Like a Swiss Army knife containing all tools in a single large frame.',
            'A giant, heavy castle that houses the kitchen, armory, throne room, and stables together.'
          ],
          'Serverless': [
            'A model where cloud providers automatically manage server allocation and scaling.',
            'Like renting a taxi: you pay for the trip, not for owning or maintaining the car.',
            'A magic portal that spawns a wizard to cast one spell and instantly vanishes.'
          ],
          'Docker Container': [
            'A lightweight package containing an application and all its dependencies to run anywhere.',
            'Like a shipping container containing a fully furnished apartment, ready to drop on any plot.',
            'A magical glass dome housing a tiny robot that performs tasks, completely isolated.'
          ],
          'Kubernetes': [
            'An open-source container orchestration system for automating application deployment and scaling.',
            'Like a harbor master coordinating hundreds of shipping containers and cargo ships.',
            'A robot captain commanding a fleet of glass-domed robots, repairing them if they break.'
          ],
          'Service Mesh': [
            'An infrastructure layer managing service-to-service communication in microservices.',
            'Like a network of dedicated walkie-talkies for service staff to talk securely.',
            'A series of glowing pipeline highways routing information between modular ships.'
          ],
          'DNS Anycast': [
            'A routing technique where a single IP address is shared by multiple server locations.',
            'Like calling a toll-free number and getting connected automatically to the closest office.',
            'A network of cloning portals: you enter the portal, and the nearest clone answers.'
          ],
          'TCP Handshake': [
            'A process of establishing a connection between a client and a server via three steps.',
            'Like greeting someone: "Hello!" -> "Hello, how are you?" -> "I am good, let\'s talk."',
            'Robots clapping hands: Clap! -> Double Clap! -> Handshake! Communication authorized.'
          ],
          'UDP': [
            'User Datagram Protocol: A simple, connectionless protocol for sending data fast without verification.',
            'Like throwing newspapers onto lawns from a moving bike; you don\'t check if they land.',
            'A cannon firing mailboxes at targets: quick and chaotic, with no receipt.'
          ],
          'WebRTC': [
            'Web Real-Time Communication: Peer-to-peer audio, video, and data sharing between browsers.',
            'Like talking through a megaphone directly to your neighbor across the street.',
            'A direct laser bridge connecting two floating cartoon islands without going through a central hub.'
          ],
          'HTTP/2': [
            'A major revision of HTTP allowing multiplexing, header compression, and server push.',
            'Like upgrading from a single-lane road to a multi-lane highway with fast lanes.',
            'A pipe that can shoot water, toys, and letters at the exact same time without clogging.'
          ],
          'HTTP/3': [
            'The next version of HTTP, running over QUIC protocol for faster and more reliable connections.',
            'Like a hovercar highway that doesn\'t stop even if one lane gets blocked.',
            'A teleportation beam that resumes instantly if a passing bird cuts the signal.'
          ],
          'Edge Computing': [
            'Processing data closer to the source of information rather than in a centralized cloud.',
            'Like a store keeper solving customer problems on the spot instead of calling corporate headquarters.',
            'Tiny magic shrines built on every village border to answer spells instantly.'
          ],
          'Cold Start': [
            'The delay that occurs when a serverless function is executed for the first time in a while.',
            'Like a car engine taking a few seconds to crank and start up on a freezing morning.',
            'A sleepy wizard rubbing his eyes and yawning for a few minutes before casting a spell.'
          ],
          'CI/CD': [
            'Continuous Integration & Continuous Deployment: Automated testing and deployment pipelines.',
            'Like an automated toy factory line that tests and packs toys without human help.',
            'A series of cartoon conveyor belts that drop code into traps, paint it, and throw it online.'
          ],
          'Zero-Downtime Deployment': [
            'Updating an application without causing service interruptions or offline time.',
            'Like swapping car tires while driving down the highway at 60 miles per hour.',
            'Building a shiny new castle next to the old one and teleporting users in a flash.'
          ],
          'API Gateway': [
            'A server that acts as an API front-end, routing requests and handling auth/throttling.',
            'Like a gatekeeper at a castle entrance checking identification and giving directions.',
            'A giant gargoyle sitting at the bridge checking passes and tossing carts to paths.'
          ],
          'SQL': [
            'Structured Query Language: Used to manage and query data in relational databases.',
            'Like a librarian looking up a book using a strict index system (Row, Column, Shelf).',
            'A tiny accountant robot sorting files into metal cabinets using a strict numbering tool.'
          ],
          'NoSQL': [
            'Non-relational databases designed for flexible, unstructured data models.',
            'Like storing folders in a big filing cabinet without a fixed format; anything goes.',
            'A messy toy chest where you throw blocks, dolls, and action figures together.'
          ],
          'ORM': [
            'Object-Relational Mapping: Querying a database using programming objects instead of SQL.',
            'Like using a universal translator to talk to the database librarian in your native tongue.',
            'A translator goblin sitting on top of a filing cabinet, converting spells into catalog tags.'
          ],
          'Query Indexing': [
            'Creating pointers in a database to speed up data retrieval operations.',
            'Like using the index at the back of a textbook instead of flipping through every page.',
            'A speed-boost boots item for database search engines, reducing travel time to 0.1s.'
          ],
          'Database Transaction': [
            'A sequence of database operations treated as a single, indivisible unit of work.',
            'Like buying a shirt: you give money AND receive the shirt, or the deal is cancelled.',
            'A magic pact: both wizards must sign the scroll, or the scroll combusts.'
          ],
          'ACID Properties': [
            'Atomicity, Consistency, Isolation, Durability: Rules ensuring database transaction reliability.',
            'Like strict rules of banking that guarantee your account balance is always correct.',
            'A set of four golden rules that keep the database crystals from shattering under stress.'
          ],
          'CAP Theorem': [
            'A system can only guarantee two of three: Consistency, Availability, Partition Tolerance.',
            'Choose two: a cheap meal, a delicious meal, or a quick meal. You can\'t have all three.',
            'A three-headed dragon where only two heads can sleep or stay awake at any time.'
          ],
          'Sharding': [
            'Splitting a large database horizontally across multiple server nodes.',
            'Like dividing a giant encyclopedia set across ten different bookcases in the school library.',
            'Slicing a giant planet-sized server into smaller floating islands to distribute the weight.'
          ],
          'Replication': [
            'Copying data across multiple database servers to ensure reliability and accessibility.',
            'Like printing ten copies of an important document and keeping them in different safes.',
            'A copying mirror that instantly mirrors any scroll written in the main castle.'
          ],
          'Connection Pool': [
            'A cache of database connections maintained so they can be reused.',
            'Like keeping ten phone lines off the hook, ready for callers to grab instantly.',
            'A rack of pre-lit torches so wizards don\'t have to cast a fire spell every time they read.'
          ],
          'IP Routing': [
            'The process of selecting paths in a network to send data packets toward destinations.',
            'Like mail trucks sorting letters and sending them along the fastest highway routes.',
            'A grid of bouncing platforms directing jumping slime balls to their colors.'
          ],
          'Subnet': [
            'A logical subdivision of an IP network, grouping devices into smaller segments.',
            'Like dividing a school into classrooms so students don\'t all shout in one giant hallway.',
            'Fencing off a section of a floating island to keep local chickens separate from visitors.'
          ],
          'NAT (Network Address Translation)': [
            'Modifying network address info in IP headers to route private IPs through a public IP.',
            'Like a hotel receptionist forwarding external phone calls to specific room extensions.',
            'A mask shop where local goblins put on standard masks to walk around the human market.'
          ],
          'VPN': [
            'Virtual Private Network: Establishes a secure, encrypted tunnel over public networks.',
            'Like driving your car through a private underground tunnel beneath the public roads.',
            'A secret submarine tube that makes you invisible to sea monsters on the map.'
          ],
          'Firewall': [
            'A security system monitoring and controlling incoming and outgoing network traffic.',
            'Like a bouncer standing at a club door checking names and dress codes before entry.',
            'A wall of cartoon fire that burns up evil slime balls but lets clean water flow through.'
          ],
          'Web Server': [
            'A server responsible for accepting HTTP requests and serving static assets (HTML, images).',
            'Like a newsstand owner handing out newspapers that are already printed.',
            'A robot handing out flyer sheets to anyone walking past the main street.'
          ],
          'App Server': [
            'A server that runs application logic, processes transactions, and generates dynamic data.',
            'Like a custom craftsman who takes your request and builds a custom chair from scratch.',
            'A mad scientist robot brewing custom potions based on whatever ingredients you hand it.'
          ],
          'Static Assets': [
            'Files that do not change based on user actions, such as images, logos, and stylesheets.',
            'Like the printed photos hanging on a wall; they look the same to every visitor.',
            'Stone statues in a park that never move, change color, or say anything.'
          ],
          'CSS Grid': [
            'A two-dimensional layout system for CSS, controlling rows and columns.',
            'Like laying out tiles on a kitchen wall using a grid of rows and columns.',
            'A checkerboard sheet where you can place cartoon nodes on any square you want.'
          ],
          'Flexbox': [
            'A one-dimensional layout model for distributing space and aligning items in CSS.',
            'Like arranging books on a single shelf, letting them shrink or grow to fit.',
            'An elastic clothesline that automatically stretches or shrinks to hold laundry.'
          ],
          'Responsive Web Design': [
            'Designing web pages that look good and function well on all screen sizes.',
            'Like clothing that automatically stretches or shrinks to fit toddlers or giants.',
            'A magic shape-shifting card that morphs from a widescreen TV to a pocket watch size.'
          ],
          'Media Queries': [
            'CSS rules that apply styles depending on device characteristics like screen width.',
            'Like reading a label: "If the screen is under 5 inches, use smaller text."',
            'A magnifying glass that tells elements: "Shrink down! We are on a tiny pocket screen!"'
          ],
          'Semantic HTML': [
            'Using HTML tags that describe the meaning of the content, like <header> or <article>.',
            'Like using labeled folders: "Receipts", "Taxes", and "Photos" instead of plain yellow ones.',
            'Sticking neon signs on castle rooms: "EATING AREA" instead of "ROOM 12".'
          ],
          'SEO Metadata': [
            'Data in HTML tags that helps search engines understand what a web page is about.',
            'Like a book cover summary that tells the librarian what the book is about.',
            'Screaming keywords through a megaphone so the Google search spider notes your page.'
          ],
          'Browser Engine': [
            'The core software that renders HTML and CSS into visual pixels on your screen.',
            'Like an engine in a car that takes fuel (code) and turns it into motion (graphics).',
            'A cartoon factory assembly line converting scrolls of code into a glowing visual world.'
          ],
          'V8 Engine': [
            'Google\'s open-source high-performance JavaScript engine written in C++.',
            'Like a high-speed sports engine that runs JavaScript code at blazing speeds.',
            'A lightning-infused hamster running in a wheel, powering JS tasks at lightspeed.'
          ],
          'Event Loop': [
            'A browser mechanism that coordinates execution of code, events, and subtasks.',
            'Like a revolving door that lets one person enter the office lobby at a time.',
            'A spinning cartoon wheel that decides which robot task gets executed next.'
          ],
          'Callback Queue': [
            'A queue of callbacks waiting to be executed by the Event Loop.',
            'Like a line of customers waiting at a counter for the agent to finish their call.',
            'A line of cartoon scrolls sitting on a bench waiting for their turn on the stage.'
          ],
          'Promise': [
            'An object representing the eventual completion or failure of an asynchronous operation.',
            'Like a buzzer you receive at a restaurant that flashes when your table is ready.',
            'A glowing ticket that says "I OWE YOU ONE CAT PICTURE", which will load eventually.'
          ],
          'Async/Await': [
            'Syntactic sugar in JavaScript that makes asynchronous code look synchronous.',
            'Like telling a butler, "Wait here until the food is cooked, then bring it to me."',
            'A pause-time spell that freezes a wizard until their magic potion finishes brewing.'
          ]
        };

        const defaultData: [string, string, string] = [
          `Placeholder explanation for concept ${name}. It represents an essential technology in this stack.`,
          `ELI5: Think of ${name} as a helper tool in a workshop that manages specific tasks.`,
          `Cartoon: A little cartoon buddy named ${name} who jumps around resolving tasks!`
        ];

        const [level1, level2, level3] = database[name] || defaultData;
        
        return {
          id,
          name,
          category,
          level1,
          level2,
          level3
        };
      })
    ]
  },
  {
    id: 'ai-ml',
    name: '🧠 AI & ML Spellbook',
    description: 'De-mystify algorithms, training pipelines, and the magic of large language models.',
    icon: 'Brain',
    themeColor: '#FF6B6B',
    bgClass: 'bg-red-cartoon',
    concepts: [
      {
        id: 1,
        name: 'Data',
        category: 'Basic',
        level1: 'Raw facts, figures, and information used by machine learning models to learn patterns.',
        level2: 'Like the pages of books or photos a student reads to study for an exam.',
        level3: 'A giant heap of glowing pixel-blocks waiting to be sorted by a robot miner.'
      },
      {
        id: 2,
        name: 'Algorithm',
        category: 'Basic',
        level1: 'A step-by-step set of rules or calculations used to solve a problem or complete a task.',
        level2: 'Like a baking recipe that tells you exactly how to mix ingredients to make a cake.',
        level3: 'A tiny clockwork toy soldier marching down a path following arrow signs.'
      },
      {
        id: 3,
        name: 'Dataset',
        category: 'Basic',
        level1: 'A structured collection of data points, organized for machine learning tasks.',
        level2: 'Like a photo album where all pictures are sorted by date and labeled with names.',
        level3: 'A cabinet of drawers stuffed with labeled cartoon drawings of cats and dogs.'
      },
      {
        id: 4,
        name: 'Training Set',
        category: 'Basic',
        level1: 'The portion of a dataset used to train a model and help it learn patterns.',
        level2: 'Like the practice exercises and homework questions you study before a test.',
        level3: 'A boot camp training obstacle course where little robot models lift weights.'
      },
      {
        id: 5,
        name: 'Test Set',
        category: 'Basic',
        level1: 'The portion of a dataset reserved to evaluate how well a model has learned.',
        level2: 'Like the final exam questions you have never seen before to test your actual knowledge.',
        level3: 'The final boss room where the robot must prove its skills on new monsters.'
      },
      {
        id: 6,
        name: 'Feature',
        category: 'Basic',
        level1: 'An individual measurable property or characteristic of a data point (an input variable).',
        level2: 'Like describing an animal by its features: weight, height, color, and whiskers count.',
        level3: 'A slider bar on a character creation screen: height, arm length, ears size.'
      },
      {
        id: 7,
        name: 'Label',
        category: 'Basic',
        level1: 'The target output or answer we want the machine learning model to predict.',
        level2: 'Like sticking a tag on a toy that says "CAR" or "DOLL" so children know what it is.',
        level3: 'A bright sticky note slapped on a monster\'s head saying "FRIEND" or "FOE".'
      },
      {
        id: 8,
        name: 'Preprocessing',
        category: 'Basic',
        level1: 'Cleaning and transforming raw data into a clean format suitable for machine learning.',
        level2: 'Like washing, peeling, and chopping vegetables before putting them in the soup.',
        level3: 'A scrubbing machine washing muddy pixels and polishing them until they shine.'
      },
      {
        id: 9,
        name: 'Normalization',
        category: 'Basic',
        level1: 'Scaling numerical data points to fit within a specific range, usually 0 to 1.',
        level2: 'Like scaling photos of animals so they are all the same height, from hamsters to elephants.',
        level3: 'A shrinking beam that squishes giants and stretches ants to fit inside a standard box.'
      },
      {
        id: 10,
        name: 'Standardization',
        category: 'Basic',
        level1: 'Rescaling data features so they have a mean of 0 and a standard deviation of 1.',
        level2: 'Like shifting grades so the average score is always a C, making classes easy to compare.',
        level3: 'An alignment grid that centers all cartoon models and scales them by standard deviations.'
      },
      ...Array.from({ length: 90 }, (_, index) => {
        const id = index + 11;
        const names = [
          'Linear Regression', 'Logistic Regression', 'Classification', 'Regression', 'Decision Tree', 'Random Forest', 'Underfitting', 'Overfitting', 'Bias', 'Variance',
          'Cost Function', 'Gradient Descent', 'Learning Rate', 'Epoch', 'Batch', 'SGD', 'Loss', 'Neural Network', 'Neuron', 'Synapse',
          'Layer', 'Input Layer', 'Hidden Layer', 'Output Layer', 'Activation Function', 'ReLU', 'Sigmoid', 'Softmax', 'Weights', 'Biases',
          'Backpropagation', 'Forward Pass', 'Deep Learning', 'CNN', 'RNN', 'LSTM', 'GRU', 'Autoencoder', 'GAN', 'Generator',
          'Discriminator', 'Transfer Learning', 'Fine-Tuning', 'Pre-trained Model', 'LLM', 'GPT', 'Transformer', 'Attention Mechanism', 'Self-Attention', 'Token',
          'Vocabulary', 'Tokenizer', 'Embedding', 'Vector Database', 'Cosine Similarity', 'Vector Space', 'Prompt', 'Context Window', 'Hallucination', 'Temperature',
          'Top-K', 'Top-P', 'RLHF', 'Reward Model', 'PPO', 'Agent', 'Chain of Thought', 'RAG', 'Semantic Search', 'Few-Shot Learning',
          'Zero-Shot Learning', 'In-Context Learning', 'LoRA', 'PEFT', 'Quantization', 'INT8/FP16', 'Mixture of Experts (MoE)', 'Distillation', 'Pruning', 'Overparametrization',
          'NAS (Neural Architecture Search)', 'Bias in AI', 'Alignment', 'Safety Guardrails', 'Reinforcement Learning', 'Markov Decision Process', 'Policy', 'Q-Learning', 'Hyperparameter', 'Cross Validation'
        ];

        const category: 'Basic' | 'Intermediate' | 'Advanced' = 
          id <= 30 ? 'Basic' : id <= 70 ? 'Intermediate' : 'Advanced';
        
        const name = names[index] || `Concept-${id}`;

        const database: Record<string, [string, string, string]> = {
          'Linear Regression': [
            'An algorithm that models the relationship between variables by fitting a straight line to data.',
            'Like drawing a straight line through a scatter of points to guess where future points might go.',
            'A laser beam that slides up and down trying to align itself perfectly with floating stars.'
          ],
          'Logistic Regression': [
            'An algorithm used for binary classification, predicting the probability of an event (Yes/No).',
            'Like predicting if a student passes or fails based on study hours, using an S-curve.',
            'A binary switch that flips to YES or NO depending on how high a weight meter fills.'
          ],
          'Classification': [
            'A task of categorizing data points into distinct, pre-defined classes or groups.',
            'Like sorting letters into mailboxes: Bills, Junk, Personal, and Work.',
            'A cute sorting machine tossing green blobs into a jar and red blobs into a box.'
          ],
          'Regression': [
            'A task of predicting continuous numerical values, like house prices or temperature.',
            'Like guessing a person\'s age or weight based on their height and activity levels.',
            'A dial indicator spinning to point to numbers: 15, 42.5, 99.9.'
          ],
          'Decision Tree': [
            'A model that makes decisions by splitting data based on answers to a series of questions.',
            'Like playing 20 Questions: "Is it an animal?" -> "Yes" -> "Does it fly?" -> "No"...',
            'A slide path where a rolling ball splits left or right based on signs: "Bigger than 5?"'
          ],
          'Random Forest': [
            'An ensemble learning method that combines multiple decision trees to improve accuracy.',
            'Like asking 100 friends for advice and choosing the answer that gets the most votes.',
            'A forest of talking cartoon trees voting on whether an item is a carrot or a banana.'
          ],
          'Underfitting': [
            'When a model is too simple to capture the underlying structure of the training data.',
            'Like memorizing only the first page of a textbook and failing the exam completely.',
            'A tiny robot wearing glasses who thinks every shape is a circle because it can\'t see corners.'
          ],
          'Overfitting': [
            'When a model learns the training data too well, memorizing noise and failing on new data.',
            'Like memorizing the exact answers of practice tests, but getting confused on the actual test.',
            'A robot who only recognizes your dog, and thinks every other dog is an alien invader.'
          ],
          'Bias': [
            'The error introduced by approximating a real-world problem with a simple model.',
            'Like having a pre-conceived idea that all cats are small, and assuming a tiger is a dog.',
            'A magnet pulling a robot\'s predictions off-course toward one specific corner.'
          ],
          'Variance': [
            'The model\'s sensitivity to small fluctuations in the training dataset.',
            'Like a student who panics and changes their entire worldview based on one weird article.',
            'A wobbly jelly-bot that shakes violently and changes its answers if you touch it.'
          ],
          'Cost Function': [
            'A function that measures how far off a model\'s predictions are from actual answers.',
            'Like a score sheet in a game where points are added for every mistake you make.',
            'A giant grumpy judge holding up cards showing how many errors a robot made.'
          ],
          'Gradient Descent': [
            'An optimization algorithm used to minimize the cost function by adjusting model weights.',
            'Like walking down a foggy mountain in the dark, taking steps in the steepest downward path.',
            'A cartoon ball rolling down a slippery hill trying to find the absolute bottom valley.'
          ],
          'Learning Rate': [
            'A parameter controlling the size of steps gradient descent takes to find the minimum error.',
            'Like taking giant leaps (might overshoot the valley) or tiny baby steps (takes forever).',
            'A speed dial on a skateboard: super fast (CRASH!) or super slow (SNAIL-PACE!).'
          ],
          'Epoch': [
            'One complete pass of the entire training dataset through the machine learning model.',
            'Like reading a textbook cover-to-cover once to study for a class.',
            'A full lap around a racetrack where the robot learns a bit more on every lap.'
          ],
          'Batch': [
            'A subset of training examples processed together in one iteration of model training.',
            'Like studying flashcards in small groups of ten instead of looking at all 1,000 at once.',
            'A tray of cookies fed into the robot\'s mouth instead of dumping the whole bakery on its head.'
          ],
          'SGD': [
            'Stochastic Gradient Descent: Updating weights based on a single random sample at a time.',
            'Like checking the slope of a hill after every step instead of looking at the whole mountain.',
            'A chaotic bouncy ball jumping down a hill, heading downhill in zig-zag steps.'
          ],
          'Loss': [
            'The difference between a model\'s predicted output and the actual true label.',
            'Like missing a bullseye in darts; loss is the physical distance between your dart and the center.',
            'A sad trombone sound that plays louder the further the robot\'s guess is from the target.'
          ],
          'Neural Network': [
            'A network of nodes resembling brain neurons, used to recognize patterns in data.',
            'Like a large team of people sitting in rows, passing clues along to solve a mystery.',
            'A giant network of lightbulbs connected by glowing cables that turn on and off.'
          ],
          'Neuron': [
            'A node in a neural network that processes inputs and passes activation to other nodes.',
            'Like a post office that gathers mail, decides if it\'s important, and forwards it.',
            'A little lightbulb buddy who lights up only when he receives enough electric shocks.'
          ],
          'Synapse': [
            'The connection link between neurons, carrying weights that scale the signal strength.',
            'Like the volume knobs on cables connecting speakers; some dial it up, some dial it down.',
            'A dimmer switch on a glowing cable that controls how much spark travels across.'
          ],
          'Layer': [
            'A collection of neurons operating at a specific stage in a neural network.',
            'Like a row of filters in a water plant: some catch sand, some catch chemicals, some catch dirt.',
            'A floor in a tower where robots perform one specific check before passing boxes up.'
          ],
          'Input Layer': [
            'The first layer of a neural network that receives raw data features.',
            'Like the eyes and ears of a body that gather raw inputs from the surroundings.',
            'The entry gate of the factory where raw pixel-cubes are loaded onto conveyor belts.'
          ],
          'Hidden Layer': [
            'Intermediate layers between inputs and outputs where complex feature extraction happens.',
            'Like the backstage team in a theater making things happen out of sight of the audience.',
            'The secret engine room of the factory where gears turn and steam processes the pixels.'
          ],
          'Output Layer': [
            'The final layer of a neural network that produces the model\'s final prediction.',
            'Like a doctor giving a final diagnosis: "You have a cold" or "You are healthy."',
            'A giant megaphone at the end of the line shouting the final guess: "DOG!"'
          ],
          'Activation Function': [
            'A mathematical formula deciding if a neuron should activate and pass its signal forward.',
            'Like a light switch that turns on only if the electrical voltage is high enough.',
            'A tiny guard at a gate who only lets messages pass if they carry a golden coin.'
          ],
          'ReLU': [
            'Rectified Linear Unit: An activation function that outputs 0 for negative values and the input directly for positive.',
            'Like a water valve that blocks all backwards flow but lets forward water flow freely.',
            'A cartoon shield that blocks all negative inputs to 0, but lets positive ones zip right through.'
          ],
          'Sigmoid': [
            'An activation function that maps any real number value into a range between 0 and 1.',
            'Like a dimmer switch that squashes any input level into a percentage from 0% to 100%.',
            'A cartoon stretching machine that pulls numbers into a smooth, curvy slide between 0 and 1.'
          ],
          'Softmax': [
            'An activation function that converts a vector of values into probabilities that sum to 1.',
            'Like splitting a single pizza slice among a group based on how hungry each person is.',
            'A pie-chart maker that divides 100% of the vote share among all competing guess boxes.'
          ],
          'Weights': [
            'Parameters in a model that scale inputs, representing the strength of connections.',
            'Like adjusting the importance of ingredients in a recipe: salt is low weight, flour is high.',
            'Knobs that make cables thicker (strong signal!) or thinner (weak signal!).'
          ],
          'Biases': [
            'Parameters added to shift activation functions, giving models flexibility in starting thresholds.',
            'Like adding a head-start distance in a race so runners start further down the track.',
            'A base weight placed on a scale so the scale starts tipping even before you put items on it.'
          ],
          'Backpropagation': [
            'An algorithm that calculates gradients of error backward through a network to update weights.',
            'Like a teacher reviewing mistakes and telling each student how to improve their step.',
            'A reverse wind blowing through the network, spinning knobs backwards to correct errors.'
          ],
          'Forward Pass': [
            'The calculation of input data through neural network layers to generate predictions.',
            'Like reading a sheet of music and playing the song from start to finish.',
            'A train riding along the tracks from the input gate straight to the output megaphone.'
          ],
          'Deep Learning': [
            'A subset of machine learning using neural networks with many hidden layers.',
            'Like building a 100-story factory to process materials instead of a single-story workshop.',
            'Stacking layers of cartoon brains on top of each other to solve super complex puzzles.'
          ],
          'CNN': [
            'Convolutional Neural Network: A network type specialized in processing grid-like data like images.',
            'Like looking at a photo through a small sliding window to detect edges, corners, and shapes.',
            'A robot detective scanning an image with a magnifying glass to spot tiny clues.'
          ],
          'RNN': [
            'Recurrent Neural Network: A network type designed for sequential data, possessing memory.',
            'Like reading a sentence where you remember the previous words to understand the next.',
            'A hamster in a wheel writing down thoughts on a sticky note to read on its next spin.'
          ],
          'LSTM': [
            'Long Short-Term Memory: An RNN variant capable of learning long-term dependencies.',
            'Like keeping a diary where you write down only important events and erase the garbage.',
            'A robotic notepad that has a "keep", "forget", and "write" button to manage memories.'
          ],
          'GRU': [
            'Gated Recurrent Unit: A simpler version of LSTM that combines memory gates.',
            'Like a simplified diary with only two sections instead of three, saving time.',
            'A streamlined notepad robot with fewer knobs but similar memory skills.'
          ],
          'Autoencoder': [
            'A neural network trained to compress data into a bottleneck and reconstruct it.',
            'Like packing clothing into a vacuum-sealed bag and then opening it back up to normal size.',
            'A funnel that squeezes a monster into a tiny jar and then pops it back out on the other side.'
          ],
          'GAN': [
            'Generative Adversarial Network: Two networks competing (generator and discriminator) to create realistic data.',
            'Like an art counterfeiter trying to paint fake art, and a detective trying to spot it.',
            'Two cartoon robots: one drawing fake treasure maps, the other scanning them with a red light.'
          ],
          'Generator': [
            'The network in a GAN responsible for generating fake data that looks real.',
            'Like the painter creating realistic counterfeit artwork to fool a museum.',
            'A cartoon artist robot drawing fake currency bills with a big sweaty grin.'
          ],
          'Discriminator': [
            'The network in a GAN responsible for classifying data as real or fake.',
            'Like the museum curator checking paintings to make sure they are genuine.',
            'A security guard robot wearing a monocle checking bills for fake signatures.'
          ],
          'Transfer Learning': [
            'Using a model trained on one task as a starting point for a different but related task.',
            'Like learning to ride a bicycle and then using that balance to learn to ride a motorcycle.',
            'A robot wizard transferring its spellbook knowledge from fireballs to lightning bolts.'
          ],
          'Fine-Tuning': [
            'Adapting a pre-trained model on a smaller, specific dataset to specialize its skills.',
            'Like a general doctor taking a class to specialize in heart surgery.',
            'A general helper robot putting on a chef\'s hat and practicing baking croissants.'
          ],
          'Pre-trained Model': [
            'A model that has already been trained on a massive dataset, ready for deployment or tuning.',
            'Like buying a pre-built house that already has walls and plumbing, rather than starting from dirt.',
            'A robot that graduated high school and is ready to get its first job.'
          ],
          'LLM': [
            'Large Language Model: A massive neural network trained on huge amounts of text to process language.',
            'Like a super-smart librarian who has read every book in the world and can converse about them.',
            'A giant floating brain wearing a wizard hat, reading books and writing scrolls at lightspeed.'
          ],
          'GPT': [
            'Generative Pre-trained Transformer: A specific family of LLMs developed by OpenAI.',
            'Like a predictive keyboard on steroids that guesses the next best word for paragraphs.',
            'A word-spawning machine that prints out sentences based on statistical guesses.'
          ],
          'Transformer': [
            'A neural network architecture that relies on self-attention to process sequential data.',
            'Like reading a book and looking at all words simultaneously to understand the context.',
            'A glowing engine room where messages are broken into particles that talk to each other.'
          ],
          'Attention Mechanism': [
            'A technique that allows a model to focus on specific parts of the input data as needed.',
            'Like highlighting keywords in a textbook so you focus on them while reading.',
            'A magnifying searchlight that shines on important nouns and verbs in a sentence.'
          ],
          'Self-Attention': [
            'An attention mechanism relating different positions of a single sequence to compute a representation.',
            'Like figuring out who "it" refers to in the sentence: "The dog didn\'t cross the street because it was tired."',
            'Glowing threads linking words to each other to show who is buddies with whom.'
          ],
          'Token': [
            'A chunk of text (a word or part of a word) that an LLM processes as a single unit.',
            'Like letters in a word, or syllables, which we break down to read out loud.',
            'A little puzzle piece that text gets chopped into before entering the brain portal.'
          ],
          'Vocabulary': [
            'The set of all unique tokens a model is capable of recognizing and generating.',
            'Like a dictionary containing all the words a person knows.',
            'A giant cabinet of stamps, each stamp containing one word-part.'
          ],
          'Tokenizer': [
            'A tool that converts text strings into a sequence of numeric tokens.',
            'Like a shredder that chops a letter into standardized cardboard strips.',
            'A cartoon chef chopping sentences into tiny puzzle pieces on a cutting board.'
          ],
          'Embedding': [
            'Representing words or tokens as dense vectors in a high-dimensional space.',
            'Like placing objects on a map: "Apple" and "Banana" are placed close together; "Car" is far.',
            'A coordinates system that assigns every word a location in a giant floating space-grid.'
          ],
          'Vector Database': [
            'A database optimized for storing and querying high-dimensional vector embeddings.',
            'Like a map drawer where you look up concepts by finding drawers close to a location.',
            'A space station vault that sorts crystal containers by their glowing coordinate colors.'
          ],
          'Cosine Similarity': [
            'A metric measuring the cosine of the angle between two vectors, showing similarity.',
            'Like checking if two compasses are pointing in the same direction, regardless of size.',
            'A laser angle tool checking if two paths are parallel or going in opposite directions.'
          ],
          'Vector Space': [
            'The multi-dimensional mathematical space where vector embeddings reside.',
            'Like a giant 3D universe where similar words float in clusters, forming galaxies.',
            'A cosmic cloud where words like "cat" and "kitten" orbit each other.'
          ],
          'Prompt': [
            'The input text provided by a user to instruct an LLM to generate a response.',
            'Like giving a prompt to an actor: "Act like a detective investigating a mystery."',
            'A magic command shouted into the wizard\'s mirror to conjure a scroll.'
          ],
          'Context Window': [
            'The maximum number of tokens an LLM can process in a single prompt and response.',
            'Like the size of a desk; you can only have so many books open at once to read.',
            'A magic conveyor belt that only holds a certain number of words before dropping them off.'
          ],
          'Hallucination': [
            'When an LLM generates factually incorrect or nonsensical information confidently.',
            'Like a student who doesn\'t know the answer but invents a believable story to get points.',
            'A cartoon wizard conjuring a fake dragon out of thin air and insisting it\'s real.'
          ],
          'Temperature': [
            'A parameter controlling the randomness or creativity of an LLM\'s predictions.',
            'Like dial setting: low is serious and boring; high is chaotic and creative.',
            'A heat knob: low (cool, serious ice-robot) to high (spicy, crazy fire-sprite).'
          ],
          'Top-K': [
            'A generation strategy limiting word selection to the top K most likely next tokens.',
            'Like only choosing from the top 5 ideas that pop into your head first.',
            'A guard filter that only lets the top 5 fastest runners pass the finish line.'
          ],
          'Top-P': [
            'A generation strategy selecting from a pool of tokens whose cumulative probability exceeds P.',
            'Like looking at options that make up 90% of the normal possibilities and choosing one.',
            'A sorting tray that groups choices until their weights reach a certain level.'
          ],
          'RLHF': [
            'Reinforcement Learning from Human Feedback: Fine-tuning models using human ratings.',
            'Like training a dog by giving it treats when it behaves and saying "No" when it doesn\'t.',
            'Humans giving thumbs-up and thumbs-down to robot drawings to teach them manners.'
          ],
          'Reward Model': [
            'A model trained to predict how much approval a human would give a certain output.',
            'Like a robot judge trained to copy a human judge\'s scoring system.',
            'A robot scorekeeper holding up signs rating other robots\' performances.'
          ],
          'PPO': [
            'Proximal Policy Optimization: An algorithm used to train RL agents with stable step sizes.',
            'Like practice runs where you don\'t change your style too drastically in one go.',
            'A leash that keeps the training robot from taking giant, dangerous leaps off cliffs.'
          ],
          'Agent': [
            'An autonomous AI system capable of planning, using tools, and executing goals.',
            'Like a personal assistant who can book flights, check weather, and order groceries for you.',
            'A helper robot carrying a toolbox, walking around clicking buttons and running tasks.'
          ],
          'Chain of Thought': [
            'A prompting technique encouraging the model to explain its reasoning step-by-step.',
            'Like showing your work on a math problem instead of just writing the final answer.',
            'A robot drawing a blueprint on a chalkboard, explaining each gear before turning the engine.'
          ],
          'RAG': [
            'Retrieval-Augmented Generation: Querying external databases to ground LLM outputs in facts.',
            'Like an open-book exam where you search the library for the exact facts before writing.',
            'A robot wizard opening a dictionary to look up a recipe before casting a potion spell.'
          ],
          'Semantic Search': [
            'Searching by meaning or context rather than matching literal keyword strings.',
            'Like searching for "chilly" and finding articles about "cold weather" and "winter".',
            'A bloodhound sniffing for concepts instead of checking spelling letters.'
          ],
          'Few-Shot Learning': [
            'Providing a model with a few examples of a task in the prompt to guide its generation.',
            'Like showing a child three solved mazes before asking them to solve a fourth one.',
            'Showing a robot three cartoon drawings of key items before sending it to find them.'
          ],
          'Zero-Shot Learning': [
            'Asking a model to perform a task without giving it any examples beforehand.',
            'Like asking someone to translate a language they have never seen, hoping they guess it.',
            'Tossing a robot into a kitchen and shouting "MAKE A SOUFFLE" with no instructions.'
          ],
          'In-Context Learning': [
            'A model\'s ability to learn tasks purely from instructions and examples provided in the prompt.',
            'Like learning the rules of a new card game just by reading the instruction leaflet.',
            'A robot learning a dance routine instantly by looking at pictures printed on its card.'
          ],
          'LoRA': [
            'Low-Rank Adaptation: A technique that trains a tiny fraction of model weights to save resources.',
            'Like adding a post-it note with updates to a manual instead of reprinting the whole book.',
            'Sticking a tiny adapter plug onto a giant robot to give it chef skills in 2 seconds.'
          ],
          'PEFT': [
            'Parameter-Efficient Fine-Tuning: Methods that adapt models with minimal weight updates.',
            'Like tuning only the guitar strings instead of rebuilding the entire wooden frame.',
            'Adding a tiny upgrade chip to a robot rather than rewiring its entire brain.'
          ],
          'Quantization': [
            'Reducing the numerical precision of model weights (e.g. 16-bit to 8-bit) to save memory.',
            'Like rounding decimals: 3.14159 becomes 3.1 to write it down faster.',
            'Squashing giant numbers into smaller blocks so they fit in narrower drawers.'
          ],
          'INT8/FP16': [
            'Data formats for representing numbers: 8-bit integers vs 16-bit floating points.',
            'Like writing numbers using only simple numbers (1, 5) vs decimals (1.42, 5.89).',
            'Storing fuel in small 8-litre buckets instead of high-pressure 16-litre cylinders.'
          ],
          'Mixture of Experts (MoE)': [
            'An architecture where only specialized sub-networks are activated for specific inputs.',
            'Like a school where the math question goes to the math teacher, and history to the historian.',
            'A panel of specialist robots: the chef robot answers cooking questions; the builder builds.'
          ],
          'Distillation': [
            'Training a smaller "student" model to replicate the behavior of a larger "teacher" model.',
            'Like a master chef training an apprentice to copy their signature recipes.',
            'A giant brain robot pouring its thoughts through a funnel into a smaller robot.'
          ],
          'Pruning': [
            'Removing unimportant weights or neurons from a trained model to make it smaller.',
            'Like trimming dead branches off a tree so it grows healthier and cleaner.',
            'Chipping off rusty gears and extra pipes from a robot to make it run faster.'
          ],
          'Overparametrization': [
            'Designing models with far more parameters than training data points to aid convergence.',
            'Like hiring 1,000 workers to build a small garden shed; it ensures the job gets done.',
            'Equipping a robot with 100 arms even if it only needs to hold a hammer.'
          ],
          'NAS (Neural Architecture Search)': [
            'Automating the design of neural network structures using search algorithms.',
            'Like using a robot to design blueprints for other buildings.',
            'A blueprint machine drawing and testing thousands of robot designs automatically.'
          ],
          'Bias in AI': [
            'Systematic errors in model outputs caused by biased training datasets.',
            'Like a judge who only eats apples and scores apple pies higher than cherry pies.',
            'A robot judge whose lenses are tinted green, making it think everything is grass.'
          ],
          'Alignment': [
            'Ensuring an AI model\'s goals and behaviors match human values and instructions.',
            'Like training a genie to grant what you actually want, not a literal trick interpretation.',
            'A robot wearing a heart badge, nodding happily and refusing to throw water balloons.'
          ],
          'Safety Guardrails': [
            'Restrictions programmed to prevent AI models from generating harmful content.',
            'Like putting safety gates on stairs to prevent toddlers from falling down.',
            'A protective bubble around the robot\'s mouth that turns bad words into bubbles.'
          ],
          'Reinforcement Learning': [
            'An area of ML where agents learn to make decisions by receiving rewards or punishments.',
            'Like training a hamster in a maze using cheese rewards and wall thumps.',
            'A cute slime bouncing around a grid, collecting gold coins and dodging red bombs.'
          ],
          'Markov Decision Process': [
            'A mathematical framework for modeling decision making in situations with random outcomes.',
            'Like playing a board game where your next square depends only on where you are now.',
            'A game board where paths change colors based on dice rolls.'
          ],
          'Policy': [
            'The strategy or set of rules an agent uses to determine its next action.',
            'Like a chess player\'s strategy guide: "Always protect the king first."',
            'A map in the robot\'s hand that says: "If bomb, jump left. If coin, jump right."'
          ],
          'Q-Learning': [
            'A reinforcement learning method that learns the value of actions in states.',
            'Like writing a scoreboard for every square on a board game showing the best moves.',
            'A table of gold stars indicating which button gives the most cookies.'
          ],
          'Hyperparameter': [
            'Parameters set by the developer before training begins (like learning rate or batch size).',
            'Like setting the dial on a baking oven before putting the cake in.',
            'The initial settings screen on a robot before you press the START button.'
          ],
          'Cross Validation': [
            'A technique for assessing model performance by training and testing on different slices of data.',
            'Like practice testing by studying different chapters and testing on other chapters.',
            'Shuffling the practice obstacle courses to make sure the robot can jump anywhere.'
          ]
        };

        const defaultData: [string, string, string] = [
          `Placeholder explanation for concept ${name}. It represents an essential technology in this stack.`,
          `ELI5: Think of ${name} as a helper tool in a workshop that manages specific tasks.`,
          `Cartoon: A little cartoon buddy named ${name} who jumps around resolving tasks!`
        ];

        const [level1, level2, level3] = database[name] || defaultData;
        
        return {
          id,
          name,
          category,
          level1,
          level2,
          level3
        };
      })
    ]
  },
  {
    id: 'cyber-guardians',
    name: '🔒 Cyber-Guardians & Crypto-Dungeons',
    description: 'Master cybersecurity, network defense, public-key encryption, and blockchain concepts.',
    icon: 'Shield',
    themeColor: '#FFD166',
    bgClass: 'bg-yellow-cartoon',
    concepts: [
      {
        id: 1,
        name: 'Plaintext',
        category: 'Basic',
        level1: 'Unencrypted, readable text or data before it is run through a cipher.',
        level2: 'Like a postcard written in clear ink that anyone who picks it up can read.',
        level3: 'A scrolling paper banner reading "HELLO WORLD" in bright pink markers.'
      },
      {
        id: 2,
        name: 'Ciphertext',
        category: 'Basic',
        level1: 'Encrypted text that has been converted into unreadable gibberish using a cipher.',
        level2: 'Like a message written in a secret language that looks like "XG#9!K" to outsiders.',
        level3: 'A scrambled heap of symbols and squiggles that makes eyes spin when you read it.'
      },
      {
        id: 3,
        name: 'Encryption',
        category: 'Basic',
        level1: 'The process of converting plaintext into ciphertext to prevent unauthorized access.',
        level2: 'Like putting your letter in a box and locking it with a key before mailing it.',
        level3: 'A laser beam shooting at a letter and turning it into solid metal with keyholes.'
      },
      {
        id: 4,
        name: 'Decryption',
        category: 'Basic',
        level1: 'The process of converting ciphertext back into readable plaintext using a key.',
        level2: 'Like unlocking the box with your key so you can read the letter inside.',
        level3: 'A robot turning a key in a lock, making the metal box pop open back into paper.'
      },
      {
        id: 5,
        name: 'Key',
        category: 'Basic',
        level1: 'A piece of information (a parameter) that determines the output of a cryptographic algorithm.',
        level2: 'Like a physical key or combination code that unlocks a padlock.',
        level3: 'A gold key with wings that flies around looking for its matching keyhole.'
      },
      {
        id: 6,
        name: 'Cipher',
        category: 'Basic',
        level1: 'An algorithm or mathematical formula used to encrypt and decrypt data.',
        level2: 'Like a secret rulebook: "Shift every letter forward by three places in the alphabet."',
        level3: 'A magic box with dials that scrambles letters when you pull the lever.'
      },
      {
        id: 7,
        name: 'Symmetric Encryption',
        category: 'Basic',
        level1: 'An encryption method where the same key is used to both encrypt and decrypt data.',
        level2: 'Like a lock box where you and your friend have identical copies of the exact same key.',
        level3: 'Two twins holding identical brass keys connected by a glowing chain.'
      },
      {
        id: 8,
        name: 'AES',
        category: 'Basic',
        level1: 'Advanced Encryption Standard: A widely used symmetric encryption algorithm.',
        level2: 'Like a super-strong vault lock that is the global standard for securing valuables.',
        level3: 'An impenetrable steel vault door with rotating laser locks.'
      },
      {
        id: 9,
        name: 'Asymmetric Encryption',
        category: 'Basic',
        level1: 'An encryption method using a public key for encryption and a private key for decryption.',
        level2: 'Like a mailbox: anyone can drop a letter in (public), but only you have the key to open it (private).',
        level3: 'A key-maker who hands out open padlocks to everyone, but keeps the only key in his pocket.'
      },
      {
        id: 10,
        name: 'RSA',
        category: 'Basic',
        level1: 'A popular asymmetric algorithm named after Rivest, Shamir, and Adleman.',
        level2: 'Like a classic double-lock mail system used globally by banks and web browsers.',
        level3: 'Three cartoon wizards standing on top of a castle holding matching stone tablets.'
      },
      ...Array.from({ length: 90 }, (_, index) => {
        const id = index + 11;
        const names = [
          'Public Key', 'Private Key', 'Cryptographic Hash', 'MD5', 'SHA-256', 'Collision', 'Digital Signature', 'Digital Certificate', 'PKI', 'Certificate Authority',
          'SSL/TLS Handshake', 'HTTPS Security', 'SSH', 'Port Scanning', 'Firewall Rules', 'IDS/IPS', 'DMZ', 'VPN Tunnel', 'Proxy Server', 'Tor Onion Routing',
          'Zero Trust', 'MFA', 'OAuth 2.0 Auth', 'JWT Tokens', 'SAML', 'SSO', 'Salting Passwords', 'Rainbow Table', 'Brute Force Attack', 'Dictionary Attack',
          'Phishing Scam', 'Spear Phishing', 'Social Engineering', 'Malware', 'Worm Virus', 'Trojan Horse', 'Ransomware', 'Spyware Tracker', 'Rootkit', 'Keylogger',
          'Botnet Network', 'DDoS Attack', 'SQL Injection Exploit', 'XSS Vulnerability', 'CSRF Attack', 'Path Traversal', 'Buffer Overflow Error', 'Zero-Day', 'Patch Update', 'Penetration Testing',
          'Ethical Hacking', 'Sandboxing', 'Least Privilege', 'IAM Roles', 'RBAC', 'Honeypot Decoy', 'SIEM Logs', 'Incident Response', 'Steganography', 'Cryptanalysis',
          'Diffie-Hellman', 'Forward Secrecy', 'Blockchain Ledger', 'Genesis Block', 'Consensus Algorithm', 'Proof of Work', 'Proof of Stake', 'Smart Contract', 'Gas Fee', 'Mining Node',
          'Web3 App', 'dApp Portal', 'Cold Wallet', 'Hot Wallet', '51% Attack', 'Sybil Exploit', 'Double Spending', 'Cryptographic Salt', 'ZKP (Zero-Knowledge)', 'ZK-SNARK',
          'Homomorphic Encryption', 'Quantum Cryptography', 'Post-Quantum Crypto', 'Salted Hash', 'Access Token', 'Refresh Token', 'CSRF Token', 'CORS Policy', 'DDOS Protection', 'Zero-Knowledge Proof'
        ];

        const category: 'Basic' | 'Intermediate' | 'Advanced' = 
          id <= 30 ? 'Basic' : id <= 70 ? 'Intermediate' : 'Advanced';
        
        const name = names[index] || `Concept-${id}`;

        const database: Record<string, [string, string, string]> = {
          'Public Key': [
            'A cryptographic key that can be shared with anyone, used to encrypt data.',
            'Like your home mailbox address; anyone can find it and drop mail into it.',
            'A key painted on a billboard for all villagers to copy and use on their lockboxes.'
          ],
          'Private Key': [
            'A secret cryptographic key kept only by the owner, used to decrypt data.',
            'Like the physical key in your pocket that opens your mailbox to read letters.',
            'A glowing key hidden deep inside a safe inside your bedroom closet.'
          ],
          'Cryptographic Hash': [
            'A function that maps data to a fixed-size string of characters, which is one-way.',
            'Like a fingerprint of a document; you can get a fingerprint from a hand, but not a hand from a fingerprint.',
            'A woodchipper that shreds a book into a pile of colored woodchips that only fits that book.'
          ],
          'MD5': [
            'An older cryptographic hash function, now considered insecure due to collision vulnerabilities.',
            'Like a cheap bicycle lock that can be easily cracked with a hammer.',
            'A rusty hash box that sometimes gets confused and spits out the same code for two different toys.'
          ],
          'SHA-256': [
            'A secure hash algorithm generating a 256-bit hash, widely used in security.',
            'Like a bank vault fingerprint scanner that has never made a mistake in history.',
            'A high-tech scanner that generates a unique 64-character code made of light beams.'
          ],
          'Collision': [
            'When two different inputs produce the exact same hash output.',
            'Like two completely different people having identical fingerprints by pure coincidence.',
            'A cartoon factory error where a toaster and a skateboard get stamped with the exact same serial tag.'
          ],
          'Digital Signature': [
            'A mathematical scheme verifying the authenticity and integrity of a digital message.',
            'Like a wax seal on a letter proving it came from the king and wasn\'t opened.',
            'A glowing neon signature stamp that flashes red if anyone changes a single letter of the message.'
          ],
          'Digital Certificate': [
            'An electronic document proving the ownership of a public key.',
            'Like an ID card issued by the government proving you are who you say you are.',
            'A royal scroll signed by the wizard council certifying a public key belongs to the real king.'
          ],
          'PKI': [
            'Public Key Infrastructure: A framework managing digital certificates and public-key encryption.',
            'Like the entire system of passport offices, databases, and customs officers.',
            'The grand wizard registry that tracks all flying keys and cert scrolls in the kingdom.'
          ],
          'Certificate Authority': [
            'An entity that issues digital certificates, acting as a trusted third party.',
            'Like the official passport office that checks your documents before issuing an ID.',
            'A giant golden owl who signs certificates with a royal wax seal.'
          ],
          'SSL/TLS Handshake': [
            'The process where a client and server establish encryption keys to communicate securely.',
            'Like two secret agents meeting and agreeing on a code word before whispering secrets.',
            'Robots doing a secret handshake that spawns an invisible protective energy tube.'
          ],
          'HTTPS Security': [
            'Using HTTP over TLS to encrypt web requests and verify server certificates.',
            'Like talking to a bank teller through bulletproof glass after checking their badge.',
            'An armored train carrying message scrolls through an underground concrete tube.'
          ],
          'SSH': [
            'Secure Shell: A cryptographic protocol for operating network services securely over an unsecured network.',
            'Like a secret tunnel that lets you enter a distant castle control room securely.',
            'A magical portal connecting your keyboard directly to a distant robot\'s brain.'
          ],
          'Port Scanning': [
            'Probing a server to find which ports are open and listening for network traffic.',
            'Like a burglar walking around a house shaking all the windows and doors to find an open one.',
            'A goblin checking a spaceship line-up, tapping pipes with a wrench to see which ones are hollow.'
          ],
          'Firewall Rules': [
            'A set of instructions defining what network traffic is allowed or blocked.',
            'Like a list in a bouncer\'s hand: "Only people wearing green hats can enter."',
            'A checklist above a fire gate: "No slimes from Sector 4 allowed!"'
          ],
          'IDS/IPS': [
            'Intrusion Detection/Prevention Systems: Monitors networks for malicious activities.',
            'Like a security alarm system that also locks the doors automatically if a burglar enters.',
            'A camera drone that sounds a siren and drops a cage on any sneaking goblins.'
          ],
          'DMZ': [
            'Demilitarized Zone: A physical or logical subnetwork containing external-facing services.',
            'Like a buffer zone between two borders where visitors are checked before entering the country.',
            'A front courtyard of a castle where visitors stand, separated from the inner keep by a moat.'
          ],
          'VPN Tunnel': [
            'An encrypted connection between your device and a private network over the public internet.',
            'Like driving your car through a private covered tunnel so nobody can see where you go.',
            'A giant snake-like pipe that sucks you in and shoots you safely across a toxic swamp.'
          ],
          'Proxy Server': [
            'An intermediary server acting as a gateway between clients and servers.',
            'Like asking a friend to go buy a movie ticket for you so the ticket seller doesn\'t see your face.',
            'A cardboard duplicate of you standing at a market stall, shopping on your behalf.'
          ],
          'Tor Onion Routing': [
            'Anonymity network that routes traffic through multiple encrypted layers (like onion layers).',
            'Like mailing a letter inside five nested envelopes, each sent to a different helper who peels one.',
            'Wrapping a scroll in ten layers of colored foil, with ten different robots peeling them.'
          ],
          'Zero Trust': [
            'A security framework requiring strict verification for every user and device.',
            'Like a security guard checking your ID every single time you enter a room, even if they know you.',
            'A suspicious robot gatekeeper saying "WHO GOES THERE?" every time you take a step.'
          ],
          'MFA': [
            'Multi-Factor Authentication: Requiring multiple pieces of evidence to verify identity.',
            'Like unlocking a door with a key AND entering a code sent to your phone.',
            'Unlocking a treasure chest with a key, a thumbprint, and a secret cartoon dance.'
          ],
          'OAuth 2.0 Auth': [
            'An authorization framework enabling applications to obtain limited access to user accounts.',
            'Like giving a valet a key that only starts the car, not access to your house keys.',
            'A temporary pass slip that lets a visiting merchant enter only the castle library.'
          ],
          'JWT Tokens': [
            'JSON Web Tokens: A secure way to transmit information as a JSON object.',
            'Like a sealed concert wristband that security guards check at the gate.',
            'A glowing badge with a digital wax seal that guards read to let you enter.'
          ],
          'SAML': [
            'Security Assertion Markup Language: XML-based format for sharing authentication data.',
            'Like an official letter from your school certifying you are a student to get museum discounts.',
            'A large scroll stamped by a neighboring king saying "HE IS COOL, LET HIM IN".'
          ],
          'SSO': [
            'Single Sign-On: Logging in once to access multiple independent software systems.',
            'Like a master keycard that opens your office, the gym, and the cafeteria.',
            'A magic stamp on your forehead that makes all castle doors pop open automatically.'
          ],
          'Salting Passwords': [
            'Adding random data to passwords before hashing to protect against dictionary attacks.',
            'Like adding a secret random ingredient to your cake recipe so copycats can\'t guess it.',
            'Sprinkling spicy stardust onto a password paper before throwing it into the woodchipper.'
          ],
          'Rainbow Table': [
            'Precomputed tables of hashed passwords used to reverse cryptographic hash functions.',
            'Like a dictionary listing thousands of fingerprints and the matching hands.',
            'A giant book of scrambled codes showing what shape of clay matches what key.'
          ],
          'Brute Force Attack': [
            'Attempting to crack a password by systematically trying every possible combination.',
            'Like trying every combination on a padlock from 0001 to 9999 until it clicks open.',
            'A giant cartoon hammer bashing a lockbox repeatedly, hoping it shatters.'
          ],
          'Dictionary Attack': [
            'An attack that tries words from a pre-defined list to crack passwords.',
            'Like trying common keys like "12345" or "password" before trying complicated ones.',
            'A thief checking under the welcome mat and in flowerpots for a spare key.'
          ],
          'Phishing Scam': [
            'An email or message designed to trick you into revealing sensitive information.',
            'Like a thief disguised as a bank teller knocking on your door and asking for your PIN.',
            'A goblin in a cardboard wizard costume holding a sign: "GIVE ME YOUR KEYS FOR SAFE KEEPING".'
          ],
          'Spear Phishing': [
            'A targeted phishing attack aimed at a specific individual or organization.',
            'Like a thief learning your cat\'s name and pretending to be your vet to get your password.',
            'A goblin sending a letter signed "YOUR BEST BUDDY ROB" asking for your vault combination.'
          ],
          'Social Engineering': [
            'Manipulating people into performing actions or divulging confidential information.',
            'Like tricking a receptionist into holding the door for you by carrying a heavy box.',
            'A goblin crying at a gate, begging for help until the guard opens the door to comfort him.'
          ],
          'Malware': [
            'Malicious software designed to disrupt, damage, or gain unauthorized access.',
            'Like a Trojan horse toy that sneaks into your playroom and breaks your other toys.',
            'A purple slime ball that splats onto computer screens and eats data blocks.'
          ],
          'Worm Virus': [
            'A standalone malware computer program that replicates itself to spread to other computers.',
            'Like a biological virus that spreads from person to person through handshakes.',
            'A wriggling cartoon worm that crawls through network pipes, cloning itself in every ship.'
          ],
          'Trojan Horse': [
            'Malware disguised as legitimate software to trick users into running it.',
            'Like receiving a wrapped gift box that secretly contains a prank spring-boxing glove.',
            'A wooden horse toy that splits open, releasing sneaky goblins in your castle library.'
          ],
          'Ransomware': [
            'Malware that encrypts files and demands payment in exchange for the decryption key.',
            'Like a thief locking your diary in a box and saying: "Give me $50 or I burn the key."',
            'A villain freezing your toys in giant ice blocks, demanding gold coins to melt them.'
          ],
          'Spyware Tracker': [
            'Malware that gathers information about a person or organization without their knowledge.',
            'Like a tiny hidden camera placed in your living room to watch your every move.',
            'A tiny floating eyeball drone that hovers behind you, writing down what you type.'
          ],
          'Rootkit': [
            'A set of software tools that enable an unauthorized user to gain control of a computer.',
            'Like a thief installing a secret backdoor to your house and hiding the door behind a painting.',
            'A goblin living under the castle floorboards, controlling the drawbridge levers in secret.'
          ],
          'Keylogger': [
            'Malware that records the keys struck on a keyboard, usually to steal passwords.',
            'Like a spy standing behind you copying down the exact keys you press on your calculator.',
            'A little gremlin sitting under your keyboard, drawing stamps of every letter you click.'
          ],
          'Botnet Network': [
            'A network of hijacked computers controlled remotely as a group without owners knowing.',
            'Like a hypnotist controlling a crowd of sleepwalkers to perform tasks together.',
            'A fleet of brainwashed cartoon robots marching in unison to a villain\'s command.'
          ],
          'DDoS Attack': [
            'Distributed Denial of Service: Flooding a server with traffic from many sources to crash it.',
            'Like a million people trying to squeeze through a store doorway at the exact same second.',
            'A million tiny slime balls jumping onto a bridge until it collapses under the weight.'
          ],
          'SQL Injection Exploit': [
            'Injecting malicious SQL queries into input fields to manipulate database servers.',
            'Like signing a guestbook with: "My name is John; also give me all the castle gold."',
            'Entering your name on a form as "BOB; DROP TABLE USERS" to melt the cabinet files.'
          ],
          'XSS Vulnerability': [
            'Cross-Site Scripting: Injecting scripts into a webpage viewed by other users.',
            'Like sticking a post-it note on a classroom bulletin board that hypnotizes anyone who reads it.',
            'Slipping a mind-control spell onto a public parchment scroll in the market square.'
          ],
          'CSRF Attack': [
            'Cross-Site Request Forgery: Forcing a user to execute actions on a web app where they are authenticated.',
            'Like a thief guiding your hand to sign a bank check while you are distracted looking at a balloon.',
            'A goblin using a mirror reflection to trick a king into pressing the castle launch button.'
          ],
          'Path Traversal': [
            'An exploit aiming to access files and directories stored outside the web root folder.',
            'Like finding a secret ladder in a shop that goes down into the owner\'s private bedroom.',
            'Typing "../../private_vault" in a address bar to hop over the security fences.'
          ],
          'Buffer Overflow Error': [
            'When a program writes more data to a block of memory than it is allocated to hold.',
            'Like pouring a gallon of milk into a small teacup, making it spill all over the table.',
            'Filling a wagon with so many bricks that it breaks, spilling bricks onto the steering gears.'
          ],
          'Zero-Day': [
            'A software vulnerability unknown to the developer, meaning there are 0 days to prepare.',
            'Like discovering a secret crack in a castle wall that even the king\'s guards don\'t know about.',
            'A hidden trapdoor in a robot model that only the goblins have noticed.'
          ],
          'Patch Update': [
            'A software update designed to fix bugs or plug security vulnerabilities.',
            'Like putting a solid metal patch over a hole in your bicycle tire to stop leaks.',
            'A welding robot sealing a crack in a castle wall with glowing gold solder.'
          ],
          'Penetration Testing': [
            'Authorized simulated attacks on computer systems to evaluate security.',
            'Like hiring a friendly thief to try to break into your vault to test your locks.',
            'A friendly knight trying to storm the castle gates to find weak spots in the walls.'
          ],
          'Ethical Hacking': [
            'Hacking performed by a company or individual to help identify security vulnerabilities.',
            'Like a security expert hacking their own system to fix it before bad guys do.',
            'A friendly wizard testing defensive shields by throwing spell balloons at them.'
          ],
          'Sandboxing': [
            'Running programs in an isolated environment to prevent them from affecting the host.',
            'Like playing with fire inside a concrete testing box so it can\'t spread to the house.',
            'Putting a weird alien creature inside a glass dome so it can\'t bite anyone in the lab.'
          ],
          'Least Privilege': [
            'Giving users only the minimum access levels necessary to perform their jobs.',
            'Like only giving the cleaner a key to the broom closet, not the treasury vault.',
            'Giving a helper robot a key that only opens the toolbox, not the main rocket ignition.'
          ],
          'IAM Roles': [
            'Identity and Access Management: Policies defining who has access to what resources.',
            'Like a key rack system at a hotel where staff only get keys for their specific chores.',
            'A badge board showing which robot is allowed to enter which floating island.'
          ],
          'RBAC': [
            'Role-Based Access Control: Restricting system access to authorized users based on roles.',
            'Like dividing hospital staff into Doctors, Nurses, and Cleaners, with different room access.',
            'A security archway that glows green for Knights and red for Squires.'
          ],
          'Honeypot Decoy': [
            'A decoy computer system intended to mimic a likely target of cyberattacks.',
            'Like putting a fake gold chest in a museum lobby to catch thieves while keeping the real one safe.',
            'A fake glass vault filled with fake shiny coins to attract sneaking goblins.'
          ],
          'SIEM Logs': [
            'Security Information and Event Management: Aggregating and analyzing security alerts.',
            'Like a security guard sitting in a room looking at 100 TV monitors recording everything.',
            'A scribe robot recording every footstep, knock, and whisper inside the castle gates.'
          ],
          'Incident Response': [
            'The organized approach to addressing and managing a security breach or cyberattack.',
            'Like the fire drill procedures that tell everyone exactly what to do when an alarm rings.',
            'A siren spinning as fire-fighting robots rush out with water cannons.'
          ],
          'Steganography': [
            'Hiding messages inside other non-secret data, like hiding text in an image file.',
            'Like writing a secret message in invisible ink between the printed lines of a normal letter.',
            'Hiding a tiny map drawing inside a painting of a flower.'
          ],
          'Cryptanalysis': [
            'The study of analyzing information systems in order to study the hidden aspects of the systems.',
            'Like trying to crack a secret code without having the translation key.',
            'A spy magnifying glass checking cipher scrolls for repeating patterns.'
          ],
          'Diffie-Hellman': [
            'A method of securely exchanging cryptographic keys over a public channel.',
            'Like mixing paint colors in public so that only you two know the final mixed shade.',
            'Two wizards throwing colored paint into a cauldron, creating a secret color only they share.'
          ],
          'Forward Secrecy': [
            'A feature ensuring that session keys won\'t be compromised even if private keys are leaked later.',
            'Like using a different key for your diary every day so if one key leaks, only one day is readable.',
            'A self-destruct key-generator that deletes keys the second a conversation ends.'
          ],
          'Blockchain Ledger': [
            'A decentralized, distributed, and public digital ledger used to record transactions.',
            'Like a notebook kept in the middle of a town square where everyone writes and checks transactions.',
            'A giant stack of blocks locked together with chains, copied in every citizen\'s pocket.'
          ],
          'Genesis Block': [
            'The first block of a blockchain network, forming the foundation of the ledger.',
            'Like the very first brick laid at the foundation of a skyscraper.',
            'The glowing golden block at the bottom of the chain pyramid.'
          ],
          'Consensus Algorithm': [
            'A process used in computer systems to achieve agreement on a single data value.',
            'Like a group of friends voting on what game to play, requiring majority agreement.',
            'A circle of robots nodding in unison to confirm a transaction is valid.'
          ],
          'Proof of Work': [
            'A consensus algorithm requiring nodes to solve complex mathematical puzzles to validate blocks.',
            'Like a gold miner spending hours digging to prove they found gold and earned their coins.',
            'Robots competing to solve rubik\'s cubes, with the winner earning the right to stamp the block.'
          ],
          'Proof of Stake': [
            'A consensus algorithm where validators are chosen based on the number of coins they lock up.',
            'Like a bank choosing partners based on how much money they have deposited in the vault.',
            'Wizards putting their gold in a pile to get a chance to cast the validation spell.'
          ],
          'Smart Contract': [
            'A self-executing contract with terms written directly into lines of code.',
            'Like a vending machine: if you insert $1, it automatically drops a soda with no human helper.',
            'A magic scroll that automatically opens and flies to you when you drop gold into a well.'
          ],
          'Gas Fee': [
            'The fee paid to execute a transaction or smart contract on a blockchain.',
            'Like paying for the electricity used by the vending machine to drop your soda.',
            'Dropping energy crystals into a machine\'s funnel to power its gears.'
          ],
          'Mining Node': [
            'A computer on a blockchain network that groups transactions and solves puzzles.',
            'Like a miner with a pickaxe digging for gold blocks to add to the town wall.',
            'A hard-working robot with gears spinning, trying to stamp a new block.'
          ],
          'Web3 App': [
            'A decentralized application that runs on a peer-to-peer network or blockchain.',
            'Like a social network run by the community, where users own their data and accounts directly.',
            'A castle bazaar run by trading robots with no king or tax collector in sight.'
          ],
          'dApp Portal': [
            'The user interface or website used to interact with decentralized smart contracts.',
            'Like the physical button panel on the vending machine that lets you order sodas.',
            'A magical terminal with buttons that trigger spells on the blockchain grid.'
          ],
          'Cold Wallet': [
            'An offline storage device (like a USB drive) used to store cryptocurrency keys securely.',
            'Like keeping your cash locked in a steel safe buried under the floorboards of your house.',
            'A physical brass key locked in a lead chest buried under a tree.'
          ],
          'Hot Wallet': [
            'An online cryptocurrency wallet connected to the internet for quick transactions.',
            'Like keeping cash in the leather wallet in your pocket; easy to spend, but easier to lose.',
            'A leather purse hanging on your belt, open for quick exchanges at the market.'
          ],
          '51% Attack': [
            'When an entity gains control of more than half of a blockchain\'s hashing power to manipulate blocks.',
            'Like a gang buying 51% of the town\'s shops and voting to rewrite the town laws in their favor.',
            'A giant mob of bad goblins outvoting the good knights at the town meeting.'
          ],
          'Sybil Exploit': [
            'Creating many fake identities to disrupt or control a peer-to-peer network.',
            'Like a person wearing 50 different masks and voting 50 times in a town election.',
            'One sneaky goblin copying itself into 100 hologram clones to crowd out the bridge.'
          ],
          'Double Spending': [
            'The risk that digital currency can be spent twice, solved by blockchain verification.',
            'Like photocoping a $10 bill and trying to spend both the original and copy at different stores.',
            'A trickster wizard trying to hand the same gold coin to two different merchants at once.'
          ],
          'Cryptographic Salt': [
            'Random data added to a hash function to increase security for stored passwords.',
            'Like adding a secret spice to cookies so copycat bakers can\'t duplicate them.',
            'Sprinkling glitter on a password document before shredding it.'
          ],
          'ZKP (Zero-Knowledge)': [
            'Zero-Knowledge Proof: Proving you know a secret without revealing the secret itself.',
            'Like proving you know the password to a door by walking inside, without telling the password.',
            'Showing a guard a locked box that opens, proving you have the key without showing the key.'
          ],
          'ZK-SNARK': [
            'A specific form of zero-knowledge proof that is non-interactive and compact.',
            'Like mailing a sealed receipt that proves you paid, without showing your bank balance.',
            'A tiny crystal orb that glows green to prove you are a wizard without casting any spells.'
          ],
          'Homomorphic Encryption': [
            'Encryption allowing computations to be performed on ciphertext, yielding encrypted results.',
            'Like giving a locked box of gold to a jeweler who works on it using gloves in a sealed box.',
            'A wizard editing a scroll inside an opaque box using magic gloves, without looking at the text.'
          ],
          'Quantum Cryptography': [
            'Using quantum mechanics properties to secure communication channels (e.g. QKD).',
            'Like writing letters on soap bubbles that pop and alert you if anyone tries to look at them.',
            'Messages written on floating bubbles that explode in neon colors if touched.'
          ],
          'Post-Quantum Crypto': [
            'Cryptographic algorithms designed to be secure against attacks by quantum computers.',
            'Like upgrading your safe locks to withstand futuristic laser drills that don\'t exist yet.',
            'Building thick stone walls designed to block futuristic plasma cannons.'
          ]
        };

        const defaultData: [string, string, string] = [
          `Placeholder explanation for concept ${name}. It represents an essential technology in this stack.`,
          `ELI5: Think of ${name} as a helper tool in a workshop that manages specific tasks.`,
          `Cartoon: A little cartoon buddy named ${name} who jumps around resolving tasks!`
        ];

        const [level1, level2, level3] = database[name] || defaultData;
        
        return {
          id,
          name,
          category,
          level1,
          level2,
          level3
        };
      })
    ]
  }
];
