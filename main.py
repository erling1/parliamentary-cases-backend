import requests
import xmltodict
import json
from pandas import DataFrame
import re



class Voterings_Oversikt_Stortinget:

    def __init__(self, sakID: str):
        self.saksID = sakID
        

    
    def get_response(self,url):

        respons =  requests.get(url)
        
        xml_file = respons.text
        data_dict = xmltodict.parse(xml_file)
        
        return data_dict
    
    def finn_alle_saker(self):
        url = 'https://data.stortinget.no/eksport/voteringsresultat'

        data_dict = self.get_response(url=url)

    def finn_votering_id_tema(self):
        url = f'https://data.stortinget.no/eksport/voteringer?sakid={self.saksID}'

        voterings_dict = self.get_response(url)

        saker_stemt_over = voterings_dict['sak_votering_oversikt']

        votering_id = []
        votering_tema = []


        if isinstance(saker_stemt_over['sak_votering_liste']['sak_votering'],list):

            for sak in saker_stemt_over['sak_votering_liste']['sak_votering']:
                votering_id.append(sak['votering_id'])
                votering_tema.append(sak['votering_tema'])

        elif isinstance(saker_stemt_over['sak_votering_liste']['sak_votering'], dict):
            
    
            votering_id.append(saker_stemt_over['sak_votering_liste']['sak_votering']['votering_id'])
            votering_tema.append(saker_stemt_over['sak_votering_liste']['sak_votering']['votering_tema'])


        return (votering_id, votering_tema)
    
  
            
    def _saks_informasjon(self, voteringID: int, votering_tema: str):

        url = f"https://data.stortinget.no/eksport/voteringsforslag?voteringid={voteringID}"
        data_dict = self.get_response(url=url)

    
        # Since voteringsforslag is a list, we need to access its first element if we want just one proposal
        forslag_tekst = data_dict['voteringsforslag_oversikt']['voteringsforslag_liste']['voteringsforslag']

       

        forslag_forslag_tekst_dict = {}

        # If forslag_tekst is a list
        if isinstance(forslag_tekst, list):
          

            forslag_forslag_tekst_dict[votering_tema] = []
            for i in range(len(forslag_tekst)):

                clean_text = re.sub('<[^<]+?>', '', forslag_tekst[i]['forslag_tekst'])
                    
                clean_text = ' '.join(clean_text.split())
                
                forslag_forslag_tekst_dict[votering_tema].append(clean_text)

        else:
            
            # Just clean the single proposal text
            clean_text = re.sub('<[^<]+?>', '', forslag_tekst['forslag_tekst'])

           
            
            clean_text = ' '.join(clean_text.split())

            


            forslag_forslag_tekst_dict[votering_tema] = clean_text

    
        return forslag_forslag_tekst_dict



    def resultat(self):
        #SAK= 83657
        votering_ids, votering_temaer = self.finn_votering_id_tema()
        enstemmig_vedtatt = False
        

       

        voterings_oversikt_sak_representanter = {}
        informasjon_om_hvertforslag = {}

        for idx, vote_id in enumerate(votering_ids):
            
            url = f'https://data.stortinget.no/eksport/voteringsresultat?VoteringId={vote_id}'
            data_dict = self.get_response(url=url)

            voteringsresultat_oversikt = data_dict['voteringsresultat_oversikt']


            



            voteringsresultat_liste = voteringsresultat_oversikt['voteringsresultat_liste']

            self.voteringsresultat_liste = voteringsresultat_liste

            if not  voteringsresultat_liste:
                print(f"Skipping empty voteringsresultat for vote_id: {vote_id}")
                print(voteringsresultat_oversikt)
                enstemmig_vedtatt =  True
                continue

            representant_voteringsresultat = voteringsresultat_liste['representant_voteringsresultat']
            

            

            stemme = []
            representant = []
            parti = []
            navn = []
            index = 0
            for index, ele in enumerate(representant_voteringsresultat):
                stemme.append(ele['votering'])
                fornavn = ele['representant']['fornavn']
                etternavn = ele['representant']['etternavn']
                fult_navn = fornavn + " " + etternavn
                navn.append(fult_navn)
                parti.append(ele['representant']['parti']['navn'])

            oversikt_dict = dict(navn=navn, parti=parti, votering=stemme)


            voterings_oversikt_sak_representanter[votering_temaer[idx]] = oversikt_dict


            info_tekst_hvert_forslag = self._saks_informasjon(vote_id,votering_temaer[idx])

            informasjon_om_hvertforslag[votering_temaer[idx]] = info_tekst_hvert_forslag[votering_temaer[idx]]

        
        
        return voterings_oversikt_sak_representanter, informasjon_om_hvertforslag, enstemmig_vedtatt

#funker ikke: 97332


#funker : 84119


#test = Voterings_Oversikt_Stortinget(97332)

#test.resultat()



"""
oversikt = test.resultat()[0]
info = test.resultat()[1]
    
#if not oversikt:

  
proposal = {}
    
for key in oversikt.keys():

    print('key', key)

    voting_data = {
            'representatives': [],
            'information' : info,
            'proposedBy' : 'proposed_by'
        }
        
    print(oversikt[key]["navn"])

    for i in range(len(oversikt[key]["navn"])):
        rep = {
                'name': oversikt[key]['navn'][i],
                'party': oversikt[key]['parti'][i],
                'vote': oversikt[key]['votering'][i]
            }
        voting_data['representatives'].append(rep)
        
    voting_data['voting_counts'] = {
                        'for': sum(1 for rep in voting_data['representatives'] if rep.get('vote', '').lower() == 'for'),
                        'mot': sum(1 for rep in voting_data['representatives'] if rep.get('vote', '').lower() == 'mot'),
                        'ikke_tilstede': sum(1 for rep in voting_data['representatives'] if rep.get('vote', '').lower() == 'ikke_tilstede')
                    }
        
    proposal[key] = voting_data
print('keys: ', proposal.keys())

print('proposal HEEEEELLLLLLOOOOOOO',proposal['Alternativ votering mellom innstillingen og forslagene 1-5 fra Ap, Sp og SV.']['voting_counts'])
"""