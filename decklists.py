from dataclasses import dataclass, field
from ability import Ability,HealingTriggeredAbility

@dataclass
class Decklist:
    name: str
    cards: list

@dataclass(frozen=True)
class Card:
    num: str
    name: str
    abilities: tuple
    def __hash__(self):
        return hash(self.num)

    def __str__(self):
        return f"{self.name}"


@dataclass(frozen=True)
class CharacterCard(Card):
    subtext: str
    description: str
    strength: int
    willpower: int
    lore: int
    cost: int
    color: str
    inkable: bool
    keywords: tuple

    def __str__(self):
        return f"{self.name} - {self.subtext}"

@dataclass(frozen=True)
class ActionCard(Card):
    description: str
    cost: int
    color: str
    is_song: bool
    inkable: bool

@dataclass(frozen=True)
class ItemCard(Card):
    description: str
    cost: int
    color: str
    inkable: bool


olaf = CharacterCard("52/204-EN-1", "Olaf", tuple(),"Friendly Snowman", "", 1, 3, 1, 1, "amethyst", True,())
pascal = CharacterCard("53/204-EN-1", "Pascal", tuple(), "Rapunzel's Companion", "While you have another character in play, "
        "this character gains Evasive", 1,1,1,1, "amethyst", True,())
moana = CharacterCard("14/204-EN-1","Moana", tuple(), "Of Motunui", "Whenever this character quests, you may ready your other princess characters. They can't quest for the rest of the turn.", 1,6,3,5,"amber",True,())
mickey_mouse = CharacterCard("51/204-EN-1","Mickey Mouse", tuple(), "Wayward Sorcerer", "You pay 1 cost less to play Broom characters.   Whenever one of your Broom characters is banished in a challenge, you may return that card to your hand", 3,4,2,4,"amethyst", True,())
wardrobe = CharacterCard("57/204-EN-1", "The Wardrobe", tuple(), "Belle's Confidant", "", 3,4,1,3,"amber", True, ())
dinglehopper = ItemCard("32/204-EN-1","Dinglehopper", (HealingTriggeredAbility(),), "Remove up to 1 damage from chosen character", 1, "amber", True)
magic_broom = CharacterCard("47/204-EN-1", "Magic Broom", tuple(), "Bucket Brigade", "When you play this character, you may shuffle a card from any discard into it's player's deck", 2,2,1,2,"amethyst",True,())
stitch = CharacterCard("22/204-EN-1", "Stitch", tuple(), "New Dog", "", 2,2,1,1,"amber", True,())
hades = CharacterCard("6/204-EN-1", "Hades", tuple(), "Lord of the Underworld", "When you play this character, return a character card from your discard pile to your hand.", 3,2,1,4,"amber", False,())
part_of_your_world = ActionCard("30/204-EN-1", "Part of your World", tuple(), "Return a character card from your discard to your hand.", 3, "amber", True,False)
heihei = CharacterCard("7/204-EN-1", "HeiHei", tuple(), "Boat Snack", "Support", 1,2,1,1,"amber",True,())
mickey_mouse_true_friend = CharacterCard("12/204-EN-1", "Mickey Mouse", tuple(), "True Friend", "", 3,3,2,3, "amber", True,())
minnie_mouse = CharacterCard("13/204-EN-1","Minnie Mouse", tuple(), "Beloved Princess", "", 2,3,1,2,"amber", True,())
control_your_temper = ActionCard("26/204-EN-1", "Control Your Temper", tuple(), "Chosen character gets -2 this turn.", 1,"amber", False,True) 
yzma = CharacterCard("60/204-EN-1", "Yzma", tuple(), "Alchemist", "Whenever this character quests, look at the top card of your deck.  Put it on either the top or the bottom of your deck.", 2,2,1,2,"amethyst", True,())
ariel = CharacterCard("1/204-EN-1", "Ariel", tuple(), "On Human Legs", "This character can't sing songs.", 3,4,2,4,"amber", True,())
maximus=CharacterCard("11/204-EN-1", "Maximus", tuple(), "Relentless Pursuer", "When you play this character, chosen character gets -2 strength this turn", 3,3,1,3,"amber", True,())
dr_facilier = CharacterCard("38/204-EN-1", "Dr. Facilier", tuple(), "Charlatan", "Challenger +2", 0,4,1,2,"amethyst", True, ("Challenger +2",))
jafar = CharacterCard("45/204-EN-1", "Jafar", tuple(), "Wicked Sorcerer", "Challenger +3", 2,5,1,4,"amethyst", True,("Challenger +3",))
maleficent = CharacterCard("49/204-EN-1", "Maleficent", tuple(), "Sorceress", "When you play this character"
        "you may draw a card.", 2,2,1,3,"amethyst", True,())
friends_on_the_other_side = ActionCard("64/204-EN-1", "Friends On The Other Side", tuple(), "Draw 2 cards", 3,"amethyst", True,True)
be_our_guest = ActionCard("25/204-EN-1", "Be Our Guest",  tuple(), "Look at the top 4 cards of your deck.  You may reveal a character card and put it into your hand.  Put the rest on the bottom of your deck in any order.",  2, "amber", True, True)
rafiki = CharacterCard("54/204-EN-1", "Rafiki", tuple(), "Mysterious Sage", "Rush", 3,3,1,3, "amethyst", False,())
sven=CharacterCard("55/204-EN-1", "Sven", tuple(), "Official Ice Deliverer", "", 5,7,1,6,"amethyst", True,())
flotsam=CharacterCard("43/204-EN-1", "Flotsam", tuple(), "Ursula's Spy", "Rush.  Your characters named Jetsam gain Rush.",
            3,4,2,5,"amethyst", False,())
jetsam=CharacterCard("46/204-EN-1", "Jetsam", tuple(), "Ursula's Spy", "Evasive.  Your characters named Flotsam gain Evasive", 3,3,1,4,"amethyst", True,("Evasive",))
hakuna_matata=ActionCard("27/204-EN-1", "Hakuna Matata",  tuple(), "Remove up to 3 damage from each of your characters.",  4, "amber", True,True)
dr_facilier7=CharacterCard("37/204-EN-1", "Dr. Facilier", tuple(), "Agent Provocateur", "Shift 5.  "
    "Whenever one of your other characters is banished in a challenge, "
    "you may return that card to your hand.", 4,5,3,7,"amethyst", False,())
cinderella=CharacterCard("3/204-EN-1", "Cinderella", tuple(), "Gentle and Kind", "Singer 5. Exert - Remove up to 3 damage from chosen Princess character.", 2,5,2,4,"amber", True,())

amber_amethyst = Decklist("Amber/Amethyst",[
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

captain_hook = CharacterCard("174/204-EN-1", "Captain Hook", tuple(), "Forceful Duelist", "Challenger +2",
        1,2,1,1,"steel",True, ("Challenger +2",))
aurora = CharacterCard("139/204-EN-1", "Aurora", tuple(), "Dreaming Guardian", "Shift 3. Your other characters gain Ward.", 3,5,2,5,"sapphire", True,())
maleficent = CharacterCard("150/204-EN-1", "Maleficent", tuple(), "Sinister Visitor", "", 3,4,2,4,"sapphire", True,())
simba = CharacterCard("189/204-EN-1", "Simba", tuple(), "Returned King", "Challenger +4. During your turn, this character gains Evasive.",
        4,6,2,7,"steel", True, ("Challenger +4",))
scar_blue = CharacterCard("158/204-EN-1", "Scar", tuple(), "Mastermind", "When you play this character, chosen opposing character gets -5 strength this turn.", 5,4,2,6,"sapphire", True,())
one_jump_ahead = ActionCard("164/204-EN-1", "One Jump Ahead", tuple(), "Put the top card of your deck into your inkwell facedown and exterted", 2,"sapphire",True,False)
kristoff = CharacterCard("182/204-EN-1", "Kristoff", tuple(), "Official Ice Master", "", 3,3,2,3,"steel",True,())
frying_pan = ItemCard("202/204-EN-1", "Frying Pan", tuple(), "Banish this item - Chosen character can't challenge during their next turn.", 2,"steel",True)
flounder = CharacterCard("145/204-EN-1", "Flounder", tuple(), "Voice of Reason", "", 2,2,1,1,"sapphire",True,())
fire_the_cannons = ActionCard("197/204-EN-1", "Fire the Cannon!",  tuple(), "Deal 2 damage to chosen character", 1,"steel",False,False)
coconut_basket = ItemCard("166/204-EN-1", "Coconut Basket",  tuple(), "Whenever you play a character, "
        "you may remove up to 2 damage from chosen charcter.", 2,"sapphire",True)
develop_your_brain = ActionCard("161/204-EN-1", "Develop your Brain", tuple(), "Look at the top 2 cards of your deck. "
        "Put one into your hand and the other on the bottom of the deck.", 1,"sapphire",False,True)
aurora2 = CharacterCard("140/204-EN-1", "Aurora", tuple(), "Regal Princess", "", 2,2,2,2,"sapphire",True,())
hercules = CharacterCard("181/204-EN-1", "Hercules", tuple(), "True Hero", "Bodyguard", 3,3,1,3,"steel",True,())
mickey_detective = CharacterCard("154/204-EN-1", "Mickey Mouse", tuple(), "Detective", "When you play this character, "
        "you may put the top card of your deck into your inkwell facedown and exterted.",
        1,3,1,3,"sapphire",False,())
aurora4 = CharacterCard("138/204-EN-1", "Aurora", tuple(), "Briar Rose", "When you play this character, chosen character "
        "gets -2 strength this turn.", 2,5,1,4,"sapphire",True,())
jasmine = CharacterCard("148/204-EN-1", "Jasmine", tuple(), "Disguised", "", 3,3,2,3,"sapphire", True,())
goons = CharacterCard("179/204-EN-1", "Goons", tuple(), "Maleficent's Underlings", "", 2,2,1,1,"steel", True,())
prince_eric = CharacterCard("187/204-EN-1", "Prince Eric", tuple(), "Dashing and Brave", "Challenger +2", 1,3,1,2,"steel",True, ("Challenger +2",))

smash= ActionCard("200/204-EN-1", "Smash", tuple(), "Deal 3 damage to a chosen character.", 3, "steel", False,False)
beast = CharacterCard("172/204-EN-1", "Beast", tuple(), "Hardheaded", "When you play this character, you may banish chosen item",
        4,4,2,5,"steel",True,())
maui = CharacterCard("185/204-EN-1", "Maui", tuple(), "Demigod", "", 8,8,3,8,"steel", True,())
grab_your_sword = ActionCard("198/204-EN-1", "Grab Your Sword", tuple(), "Deal 2 damage to each opposing character",
        5, "steel", True,False)
maleficent5 = CharacterCard("151/204-EN-1", "Maleficent", tuple(), "Uninvited", "", 3,6,3,5,"sapphire", True,())
gramma_tala = CharacterCard("146/204-EN-1", "Gramma Tala", tuple(), "Storyteller", "When this character is banished, you may"
        " put this card into your inkwell facedown and exerted", 1,1,1,2,"sapphire",True,())
mufasa = CharacterCard("155/204-EN-1", "Mufasa", tuple(), "King of the Pride Lands", "", 4,6,3,6,"sapphire",True,())
magic_golden_flower = ItemCard("169/204-EN-1", "Magic Golden Flower", tuple(), "Banish this item - remove up to 3 damage from chosen character", 1, "sapphire", True)
simba5 = CharacterCard("190/204-EN-1", "Simba", tuple(), "Rightful Heir", "During your turn, whenever this character banishes "
        "another character in a challenge, you gain 1 lore", 3, 5, 2, 5, "steel", False,())
ransack = ActionCard("199/204-EN-1", "Ransack", tuple(), "Draw 2 cards, then choose and discard 2 cards.",
        2,"steel", False,True)

sapphire_steel = Decklist("Sapphire/Steel", [
    captain_hook,captain_hook,captain_hook,aurora,
    maleficent,maleficent,maleficent,simba,
    scar_blue,one_jump_ahead,one_jump_ahead,kristoff,
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

cruella_de_vil = CharacterCard("72/204-EN-1", "Cruella De Vil", tuple(), "Miserable As Usual", "When this character is "
        "challenged and banished, you may return chosen character to their player's hand.",
        1,3,1,2,"emerald",True,())

dragon_fire = ActionCard("130/204-EN-1", "Dragon Fire", tuple(), "Banish chosen character.", 5, "ruby", False,False)
aladdin_prince = CharacterCard("69/204-EN-1", "Aladdin", tuple(), "Prince Ali", "Ward", 2,2,1,2,"emerald",True,())
scar_red = CharacterCard("122/204-EN-1", "Scar", tuple(), "Fiery Usurper", "", 5, 3, 1, 4, "ruby", True,())
aladdin_heroic = CharacterCard("104/204-EN-1", "Aladdin", tuple(), "Heroic Outlaw", "Shift 5. During your turn, whenever this "
        "character banishes another character in a challenge, you gain 2 lore and each "
        "opponent loses 2 lore", 5, 5, 2, 7, "ruby", True,())
donald_duck = CharacterCard("108/204-EN-1", "Donald Duck", tuple(), "Boisterous Fowl", "", 2,3,1,2,"ruby", True,())
mickey_mouse_steamboat = CharacterCard("89/204-EN-1", "Mickey Mouse", tuple(), "Steamboat Pilot", "", 3,4,1,3,"emerald",True,())
sergeant_tibbs = CharacterCard("124/204-EN-1", "Sergeant Tibbs", tuple(), "Courageous Cat", "", 2,2,1,1,"ruby",True,())
iago = CharacterCard("80/204-EN-1", "Iago", tuple(), "Loud-Mouthed Parrot", "Exert - Chosen character gains Reckless during their next turn.", 1,4,1,3,"emerald",True,())
rapunzel = CharacterCard("121/204-EN-1", "Rapunzel", tuple(), "Letting Down Her Hair", "When you play this character, each "
        "opponent loses 1 lore.", 5,4,2,6, "ruby",False,())
peter_pan = CharacterCard("91/204-EN-1", "Peter Pan", tuple(), "Never Landing", "Evasive", 3,2,1,3,"emerald",True,("Evasive"))
pongo = CharacterCard("120/204-EN-1", "Pongo", tuple(), "Ol' Rascal", "Evasive", 2,3,2,4,"ruby",True,("Evasive"))
aladdin_street = CharacterCard("105/204-EN-1", "Aladdin", tuple(), "Street Rat", "When you play this character, each "
        " opponent loses 1 lore", 2,2,1,3,"ruby",True,())
duke_of_weselton = CharacterCard("73/204-EN-1", "Duke of Weselton", tuple(), "Opportunistic Official", "", 2,2,1,1,"emerald",True,())
stampede = ActionCard("96/204-EN-1", "Stampede", tuple(), "Deal 2 damage to chosen damaged character.",
        1,"emerald", False, False)
vicious_betrayal = ActionCard("100/204-EN-1", "Vicious Betrayal", tuple(), "Chosen character gets +2 strength this turn.  "
    "If a villian character is chosen, they get +3 instead.", 1, "emerald", False, True)
mother_knows_best = ActionCard("95/204-EN-1", "Mother Knows Best", tuple(), "Return chosen character to their player's hand.", 3, "emerald", True, False)
stolen_scimitar = ItemCard("102/204-EN-1", "Stolen Scimitar", tuple(), "Exert - Chosen character gets +1 strength this "
        "turn.  If a character named Aladdin is chosen, he gets +2 strength instead.", 2,
        "emerald", True)
megara = CharacterCard("87/204-EN-1", "Megara", tuple(), "Pulling the Strings", "When you play this character, "
        "chosen character gets +2 strength this turn.", 2,1,1,2, "emerald", True,())
jasper = CharacterCard("81/204-EN-1", "Jasper", tuple(), "Common Crook", "Whenever this character quests, chosen opposing character can't quest during their next turn.", 2,4,1,3,"emerald", True,())
horace = CharacterCard("79/204-EN-1", "Horace", tuple(), "No-Good Scoundrel", "", 4,3,1,3, "emerald", True,())
lefou= CharacterCard("112/204-EN-1", "Lefou", tuple(), "Instigator", "When you play this character, ready chosen character.  They can't quest for the rest of this turn.", 2,2,1,2, "ruby", True,())
hes_got_a_sword = ActionCard("132/204-EN-1", "He's Got a Sword", tuple(), "Chosen character gets +2 strength this turn.",
        1, "ruby", False,True)
mad_hatter = CharacterCard("86/204-EN-1", "Mad Hatter", tuple(), "Gracious Host", "Whenever this charaacter is challenged, you may draw a card.", 2,4,3,5, "emerald", True,())
steal_from_the_rich = ActionCard("97/204-EN-1", "Steal from the Rich", tuple(), "Whenever one of your characters quests this turn, each opponent loses 1 lore", 5, "emerald", False,False)
captain = CharacterCard("106/204-EN-1", "Captain", tuple(), "Colonel's Lieutenant", "", 6,5,1,5,"ruby",True,())
shield_of_virtue = ItemCard("135/204-EN-1", "Shield of Virtue", tuple(), "Exert, 3 Ink - Ready chosen character. They can't quest for the rest of this turn.",
        1,"ruby",True)

ruby_emerald = Decklist("Ruby/Emerald", [
    cruella_de_vil,
    dragon_fire,dragon_fire,dragon_fire,
    aladdin_prince,aladdin_prince,
    scar_red,scar_red,
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
