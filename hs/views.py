from django.shortcuts import render, get_object_or_404, redirect
from pydoc import locate
from .models import Card, Minion, Spell, Weapon, Hero, Skill
from urllib.parse import urlencode


def search(request):
    card_name_part = request.GET.get('card_name_part')
    card_list = []
    for card in Card.all_cards():
        if card_name_part in card.name:
            card_list.append(card)
    context = {
        'all_cards': card_list,
        'card_name_part': card_name_part
    }
    return render(request, 'hs/search_result.html', context)


def order(request, real_type_name):
    real_type = locate('hs.models.' + real_type_name)
    unordered_all_cards = real_type.objects.all()
    order_by = request.POST.get('ordered_by')
    ordering_dict = {}
    ordered_all_cards = []
    if order_by == 'cost':
        for card in unordered_all_cards:
            ordering_dict[str(card.id)] = card.cost
        ordering_dict = sorted(ordering_dict.items(), key=lambda item: item[1])
        for card in ordering_dict:
            ordered_all_cards.append(card[0])
    elif order_by == 'rarity':
        for card in unordered_all_cards:
            ordering_dict[str(card.id)] = card.rarity
        ordering_dict = sorted(ordering_dict.items(), key=lambda item: item[1])
        for card in ordering_dict:
            ordered_all_cards.append(card[0])
    elif order_by == 'job':
        for card in unordered_all_cards:
            ordering_dict[str(card.id)] = card.job
        ordering_dict = sorted(ordering_dict.items(), key=lambda item: item[1])
        for card in ordering_dict:
            ordered_all_cards.append(card[0])
    elif order_by == 'version':
        for card in unordered_all_cards:
            ordering_dict[str(card.id)] = card.pub_version.ordering
        ordering_dict = sorted(ordering_dict.items(), key=lambda item: item[1])
        for card in ordering_dict:
            ordered_all_cards.append(card[0])
    ordered_all_cards_str = ' '.join(ordered_all_cards)
    base_url = '../'
    query_string = urlencode({'ordered_all_cards': ordered_all_cards_str})
    url = '{}?{}'.format(base_url, query_string)
    return redirect(url, real_type_name=real_type_name)


def index(request):
    all_minions = Minion.objects.all()
    all_spells = Spell.objects.all()
    all_weapons = Weapon.objects.all()
    all_heroes = Hero.objects.all()
    all_skills = Skill.objects.all()
    context = {
        'all_minions': all_minions,
        'all_spells': all_spells,
        'all_weapons': all_weapons,
        'all_heroes': all_heroes,
        'all_skills': all_skills
    }
    return render(request, 'hs/index.html', context)


def typedetail(request, real_type_name):
    ordered_all_cards_str = request.GET.get('ordered_all_cards')
    real_type = locate('hs.models.' + real_type_name)
    if not ordered_all_cards_str:
        all_cards = real_type.objects.all()
    else:
        ordered_all_cards = ordered_all_cards_str.split()
        all_cards = []
        for card in ordered_all_cards:
            real_id = int(card)
            real_card = get_object_or_404(real_type, pk=real_id)
            all_cards.append(real_card)
    if real_type_name == 'Minion':
        type_name = '随从'
    elif real_type_name == 'Spell':
        type_name = '法术'
    elif real_type_name == 'Weapon':
        type_name = '武器'
    elif real_type_name == 'Hero':
        type_name = '英雄'
    else:
        type_name = '英雄技能'
    context = {
        'card_type': type_name,
        'all_cards': all_cards
    }
    return render(request, 'hs/typedetail.html', context)


def detail(request, real_type_name, real_id):
    real_type = locate('hs.models.' + real_type_name)
    card = get_object_or_404(real_type, pk=real_id)
    if real_type_name != 'Skill':
        card_pub_version = card.pub_version
        cost = card.cost
        effect = card.effect
        explanation = card.explanation
        image_location = 'hs/images/' + real_type_name + str(real_id) + '.png'
        if real_type_name == 'Minion':
            type_name = '随从'
            minion_type = card.type
            context_of_single_type = {
                'minion_attack': card.attack,
                'minion_health': card.health,
                'minion_type': minion_type
            }
        elif real_type_name == 'Spell':
            type_name = '法术'
            context_of_single_type = {}
        elif real_type_name == 'Weapon':
            type_name = '武器'
            context_of_single_type = {
                'weapon_attack': card.attack,
                'weapon_durability': card.durability
            }
        else:
            type_name = '英雄'
            if card.skill_cost == -1:
                hero_skill_cost = '被动'
            else:
                hero_skill_cost = card.skill_cost
            context_of_single_type = {
                'hero_armor': card.armor,
                'hero_skill_cost': hero_skill_cost,
                'hero_skill_name': card.skill_name,
                'hero_skill': card.skill
            }
        context_of_all = {
            'image_location': image_location,
            'card_id': real_id,
            'card_name': card.name,
            'card_job': card.get_jobs(),
            'card_rarity': card.rarity,
            'card_type': type_name,
            'card_cost': cost,
            'card_effect': effect,
            'card_explanation': explanation,
            'card_pub_version': card_pub_version,
            'card_real_type': real_type_name,
            'card_is_normal': card.is_normal()
        }
        context = {**context_of_all, **context_of_single_type}
    else:
        type_name = '英雄技能'
        job = card.job
        image_location = 'hs/images/' + real_type_name + str(real_id) + '.png'
        if card.cost == -1:
            skill_cost = '被动'
        else:
            skill_cost = card.cost
        context = {
            'card_name': card.name,
            'card_id': real_id,
            'card_cost': skill_cost,
            'card_effect': card.effect,
            'card_job': job,
            'card_type': type_name,
            'image_location': image_location,
            'card_real_type': 'Skill'
        }
    return render(request, 'hs/detail.html', context)
