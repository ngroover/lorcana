from dataclasses import dataclass

@dataclass
class Deck:
    name: str
    cards: list

@dataclass
class Card:
    name: str

@dataclass
class CharacterCard(Card):
    subtext: str
    description: str
    strength: int
    willpower: int
    lore: int
    cost: int
    color: str
    inkable: bool

@dataclass
class ActionCard:
    name: str
    description: str
    cost: int
    color: str
    is_song: bool
    inkable: bool

@dataclass
class ItemCard:
    name: str
    description: str
    cost: int
    color: str
    inkable: bool


olaf = CharacterCard("Olaf", "Friendly Snowman", "", 1, 3, 1, 1, "amethyst", True)
pascal = CharacterCard("Pascal", "Rapunzel's Companion", "While you have another character in play, "
        "this character gains Evasive", 1,1,1,1, "amethyst", True)
moana = CharacterCard("Moana", "Of Motunui", "Whenever this character quests, you may ready your other princess characters. They can't quest for the rest of the turn.", 1,6,3,5,"amber",True)
mickey_mouse = CharacterCard("Mickey Mouse", "Wayward Sorcerer", "You pay 1 cost less to play Broom characters.   Whenever one of your Broom characters is banished in a challenge, you may return that card to your hand", 3,4,2,4,"amethyst", True)
wardrobe = CharacterCard("The Wardrobe", "Belle's Confidant", "", 3,4,1,3,"amber", True)
dinglehopper = ItemCard("Dinglehopper", "Remove up to 1 damage from chosen character", 1, "amber", True)
magic_broom = CharacterCard("Magic Broom", "Bucket Brigade", "When you play this character, you may shuffle a card from any discard into it's player's deck", 2,2,1,2,"amethyst",True)
stitch = CharacterCard("Stitch", "New Dog", "", 2,2,1,1,"amber", True)
hades = CharacterCard("Hades", "Lord of the Underworld", "When you play this character, return a character card from your discard pile to your hand.", 3,2,1,4,"amber", False)
part_of_your_world = ActionCard("Part of your World", "Return a character card from your discard to your hand.", 3, "amber", True,False)
heihei = CharacterCard("HeiHei", "Boat Snack", "Support", 1,2,1,1,"amber",True)
mickey_mouse_true_friend = CharacterCard("Mickey Mouse", "True Friend", "", 3,3,2,3, "amber", True)
minnie_mouse = CharacterCard("Minnie Mouse", "Beloved Princess", "", 2,3,1,2,"amber", True)
control_your_temper = ActionCard("Control Your Temper", "Chosen character gets -2 this turn.", 1,"amber", False,True) 
yzma = CharacterCard("Yzma", "Alchemist", "Whenever this character quests, look at the top card of your deck.  Put it on either the top or the bottom of your deck.", 2,2,1,2,"amethyst", True)
ariel = CharacterCard("Ariel", "On Human Legs", "This character can't sing songs.", 3,4,2,4,"amber", True)
maximus=CharacterCard("Maximus", "Relentless Pursuer", "When you play this character, chosen character gets -2 strength this turn", 3,3,1,3,"amber", True)
dr_facilier = CharacterCard("Dr. Facilier", "Charlatan", "Challenger +2", 0,4,1,2,"amethyst", True)
jafar = CharacterCard("Jafar", "Wicked Sorcerer", "Challenger +3", 2,5,1,4,"amethyst", True)
maleficent = CharacterCard("Maleficent", "Sorceress", "When you play this character"
        "you may draw a card.", 2,2,1,3,"amethyst", True)
friends_on_the_other_side = ActionCard("Friends On The Other Side", "Draw 2 cards", 3,"amethyst", True,True)
be_our_guest = ActionCard("Be Our Guest",  "Look at the top 4 cards of your deck.  You may reveal a character card and put it into your hand.  Put the rest on the bottom of your deck in any order.",  2, "amber", True, True)
rafiki = CharacterCard("Rafiki", "Mysterious Sage", "Rush", 3,3,1,3, "amethyst", False)
sven=CharacterCard("Sven", "Official Ice Deliverer", "", 5,7,1,6,"amethyst", True)
flotsam=CharacterCard("Flotsam", "Ursula's Spy", "Rush.  Your characters named Jetsam gain Rush.",
            3,4,2,5,"amethyst", False)
jetsam=CharacterCard("Jetsam", "Ursula's Spy", "Evasive.  Your characters named Flotsam gain Evasive", 3,3,1,4,"amethyst", True)
hakuna_matata=ActionCard("Hakuna Matata",  "Remove up to 3 damage from each of your characters.",  4, "amber", True,True)
dr_facilier7=CharacterCard("Dr. Facilier", "Agent Provocateur", "Shift 5.  "
    "Whenever one of your other characters is banished in a challenge, "
    "you may return that card to your hand.", 4,5,3,7,"amethyst", False)
cinderella=CharacterCard("Cinderella", "Gentle and Kind", "Singer 5. Exert - Remove up to 3 damage from chosen Princess character.", 2,5,2,4,"amber", True)

amber_amethyst = Deck("Amber/Amethyst",[
    olaf,olaf,olaf, pascal, pascal,
    moana, mickey_mouse,wardrobe,wardrobe,wardrobe,
    dinglehopper,dinglehopper,dinglehopper,magic_broom,magic_broom,
    magic_broom,stitch,stitch,stitch,hades,
    part_of_your_world,heihei,heihei,mickey_mouse_true_friend, mickey_mouse_true_friend,
    mickey_mouse_true_friend,minnie_mouse,minnie_mouse,minnie_mouse,
    control_your_temper,control_your_temper, yzma,yzma,ariel,ariel,
    maximus,maximus,dr_facilier,dr_facilier,jafar,jafar,maleficent,maleficent,
    friends_on_the_other_side,friends_on_the_other_side,friends_on_the_other_side,
    be_our_guest,be_our_guest,rafiki,rafiki,rafiki,sven,flotsam,jetsam,jetsam,
    hakuna_matata,hakuna_matata,dr_facilier7, cinderella,cinderella])

captain_hook = CharacterCard("Captain Hook", "Forceful Duelist", "Challenger +2",
        1,2,1,1,"steel",True)
aurora = CharacterCard("Aurora", "Dreaming Guardian", "Shift 3. Your other characters gain Ward.", 3,5,2,5,"sapphire", True)
maleficent = CharacterCard("Maleficent", "Sinister Visitor", "", 3,4,2,4,"sapphire", True)
simba = CharacterCard("Simba", "Returned King", "During your turn, this character gains Evasive.",
        4,6,2,7,"steel", True)
scar = CharacterCard("Scar", "Mastermind", "When you play this character, chosen opposing character gets -5 strength this turn.", 5,4,2,6,"sapphire", True)
one_jump_ahead = ActionCard("One Jump Ahead", "Put the top card of your deck into your inkwell facedown and exterted", 2,"sapphire",True,False)
kristoff = CharacterCard("Kristoff", "Official Ice Master", "", 3,3,2,3,"steel",True)
frying_pan = ItemCard("Frying Pan", "Banish this item - Chosen character can't challenge during their next turn.", 2,"steel",True)
flounder = CharacterCard("Flounder", "Voice of Reason", "", 2,2,1,1,"sapphire",True)
fire_the_cannons = ActionCard("Fire the Cannon!",  "Deal 2 damage to chosen character", 1,"steel",False,False)
coconut_basket = ItemCard("Coconut Basket",  "Whenever you play a character, "
        "you may remove up to 2 damage from chosen charcter.", 2,"sapphire",True)
develop_your_brain = ActionCard("Develop your Brain", "Look at the top 2 cards of your deck. "
        "Put one into your hand and the other on the bottom of the deck.", 1,"sapphire",False,True)
aurora2 = CharacterCard("Aurora", "Regal Princess", "", 2,2,2,2,"sapphire",True)
hercules = CharacterCard("Hercules", "True Hero", "Bodyguard", 3,3,1,3,"steel",True)
mickey_detective = CharacterCard("Mickey Mouse", "Detective", "When you play this character, "
        "you may put the top card of your deck into your inkwell facedown and exterted.",
        1,3,1,3,"sapphire",False)
aurora4 = CharacterCard("Aurora", "Briar Rose", "When you play this character, chosen character "
        "gets -2 strength this turn.", 2,5,1,4,"sapphire",True)
jasmine = CharacterCard("Jasmine", "Disguised", "", 3,3,2,3,"sapphire", True)
goons = CharacterCard("Goons", "Maleficent's Underlings", "", 2,2,1,1,"steel", True)
prince_eric = CharacterCard("Prince Eric", "Dashing and Brave", "Challenger +2", 1,3,1,2,"steel",True)

smash= ActionCard("Smash", "Deal 3 damage to a chosen character.", 3, "steel", False,True)
beast = CharacterCard("Beast", "Hardheaded", "When you play this character, you may banish chosen item",
        4,4,2,5,"steel",True)
maui = CharacterCard("Maui", "Demigod", "", 8,8,3,8,"steel", True)
grab_your_sword = ActionCard("Grab Your Sword", "Deal 2 damage to each opposing character",
        5, "steel", True,False)
maleficent5 = CharacterCard("Maleficent", "Uninvited", "", 3,6,3,5,"sapphire", True)
gramma_tala = CharacterCard("Gramma Tala", "Storyteller", "When this character is banished, you may"
        " put this card into your inkwell facedown and exerted", 1,1,1,2,"sapphire",True)
mufasa = CharacterCard("Mufasa", "King of the Pride Lands", "", 4,6,3,6,"sapphire",True)
magic_golden_flower = ItemCard("Magic Golden Flower", "Banish this item - remove up to 3 damage from chosen character", 1, "sapphire", True)
simba5 = CharacterCard("Simba", "Rightful Heir", "During your turn, whenever this character banishes "
        "another character in a challenge, you gain 1 lore", 3, 5, 2, 5, "steel", False)
ransack = ActionCard("Ransack", "Draw 2 cards, then choose and discard 2 cards.",
        2,"steel", False,True)

sapphire_steel = Deck("Sapphire/Steel", [
    captain_hook,captain_hook,captain_hook,aurora,
    maleficent,maleficent,maleficent,simba,
    scar,one_jump_ahead,one_jump_ahead,kristoff,
    kristoff,frying_pan,frying_pan,flounder,flounder,
    fire_the_cannons,fire_the_cannons,fire_the_cannons,
    coconut_basket,coconut_basket,coconut_basket,
    develop_your_brain,develop_your_brain,develop_your_brain,
    aurora2,aurora2,aurora2,hercules,hercules,
    mickey_detective,mickey_detective,mickey_detective,
    aurora4,aurora4,aurora4,jasmine,jasmine, goons,goons,
    prince_eric,prince_eric,smash,smash,beast,beast,
    maui,grab_your_sword,maleficent5,gramma_tala,gramma_tala,
    mufasa,mufasa,magic_golden_flower,magic_golden_flower,simba5,simba5,
    ransack,ransack])

cruella_de_vil = CharacterCard("Cruella De Vil", "Miserable As Usual", "When this character is "
        "challenged and banished, you may return chosen character to their player's hand.",
        1,3,1,2,"emerald",True)

dragon_fire = ActionCard("Dragon Fire", "Banish chosen character.", 5, "ruby", False,False)
aladdin_prince = CharacterCard("Aladdin", "Prince Ali", "Ward", 2,2,1,2,"emerald",True)
scar = CharacterCard("Scar", "Fiery Usurper", "", 5, 3, 1, 4, "ruby", True)
aladdin_heroic = CharacterCard("Aladdin", "Heroic Outlaw", "Shift 5. During your turn, whenever this "
        "character banishes another character in a challenge, you gain 2 lore and each "
        "opponent loses 2 lore", 5, 5, 2, 7, "ruby", True)
donald_duck = CharacterCard("Donald Duck", "Boisterous Fowl", "", 2,3,1,2,"ruby", True)
mickey_mouse_steamboat = CharacterCard("Mickey Mouse", "Steamboat Pilot", "", 3,4,1,3,"emerald",True)
sergeant_tibbs = CharacterCard("Sergeant Tibbs", "Courageous Cat", "", 2,2,1,1,"ruby",True)
iago = CharacterCard("Iago", "Loud-Mouthed Parrot", "Exert - Chosen character gains Reckless during their next turn.", 1,4,1,3,"emerald",True)
rapunzel = CharacterCard("Rapunzel", "Letting Down Her Hair", "When you play this character, each "
        "opponent loses 1 lore.", 5,4,2,6, "ruby",False)
peter_pan = CharacterCard("Peter Pan", "Never Landing", "Evasive", 3,2,1,3,"emerald",True)
pongo = CharacterCard("Pongo", "Ol' Rascal", "Evasive", 2,3,2,4,"ruby",True)
aladdin_street = CharacterCard("Aladdin", "Street Rat", "When you play this character, each "
        " opponent loses 1 lore", 2,2,1,3,"ruby",True)
duke_of_weselton = CharacterCard("Duke of Weselton", "Opportunistic Official", "", 2,2,1,1,"emerald",True)
stampede = ActionCard("Stampede", "Deal 2 damage to chosen damaged character.",
        1,"emerald", False, False)
vicious_betrayal = ActionCard("Vicious Betrayal", "Chosen character gets +2 strength this turn.  "
    "If a villian character is chosen, they get +3 instead.", 1, "emerald", False, True)
mother_knows_best = ActionCard("Mother Knows Best", "Return chosen character to their player's hand.", 3, "emerald", True, False)
stolen_scimitar = ItemCard("Stolen Scimitar", "Exert - Chosen character gets +1 strength this "
        "turn.  If a character named Aladdin is chosen, he gets +2 strength instead.", 2,
        "emerald", True)
megara = CharacterCard("Megara", "Pulling the Strings", "When you play this character, "
        "chosen character gets +2 strength this turn.", 2,1,1,2, "emerald", True)
jasper = CharacterCard("Jasper", "Common Crook", "Whenever this character quests, chosen opposing character can't quest during their next turn.", 2,4,1,3,"emerald", True)
horace = CharacterCard("Horace", "No-Good Scoundrel", "", 4,3,1,3, "emerald", True)
lefou= CharacterCard("Lefou", "Instigator", "When you play this character, ready chosen character.  They can't quest for the rest of this turn.", 2,2,1,2, "ruby", True)
hes_got_a_sword = ActionCard("He's Got a Sword", "Chosen character gets +2 strength this turn.",
        1, "ruby", False,True)
mad_hatter = CharacterCard("Mad Hatter", "Gracious Host", "Whenever this charaacter is challenged, you may draw a card.", 2,4,3,5, "emerald", True)
steal_from_the_rich = ActionCard("Steal from the Rich", "Whenever one of your characters quests this turn, each opponent loses 1 lore", 5, "emerald", False,False)
captain = CharacterCard("Captain", "Colonel's Lieutenant", "", 6,5,1,5,"ruby",True)
shield_of_virtue = ItemCard("Shield of Virtue", "Exert, 3 Ink - Ready chosen character. They can't quest for the rest of this turn.",
        1,"ruby",True)

ruby_emerald = Deck("Ruby/Emerald", [
    cruella_de_vil,
    dragon_fire,dragon_fire,dragon_fire,
    aladdin_prince,aladdin_prince,
    scar,scar,
    aladdin_heroic,
    donald_duck,donald_duck,
    mickey_mouse_steamboat,mickey_mouse_steamboat,mickey_mouse_steamboat,
    sergeant_tibbs,sergeant_tibbs,sergeant_tibbs,
    iago,rapunzel,rapunzel,rapunzel,peter_pan,peter_pan,
    pongo,pongo,pongo,
    aladdin_street,aladdin_street,aladdin_street,
    duke_of_weselton,duke_of_weselton,duke_of_weselton,
    stampede,stampede,
    vicious_betrayal,vicious_betrayal,
    mother_knows_best,mother_knows_best,mother_knows_best,
    stolen_scimitar,stolen_scimitar,
    megara,megara,megara,
    jasper,jasper,
    horace,horace,horace,lefou,
    hes_got_a_sword,hes_got_a_sword,
    mad_hatter,mad_hatter,mad_hatter,
    steal_from_the_rich,
    captain, captain,
    shield_of_virtue,shield_of_virtue
    ])

decklists = [amber_amethyst, sapphire_steel, ruby_emerald]
