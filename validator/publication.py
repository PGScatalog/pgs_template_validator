from validator.generic import GenericValidator
from validator.request.connector import Connector, NotFound


class Publication():

    def __init__(self, doi, pubmed_id):
        self.doi = doi
        self.PMID = pubmed_id

    def populate_from_eupmc(self, connector: Connector):
        result = None
        try:
            result = connector.get_publication(doi=self.doi, pmid=self.PMID)
        except NotFound as e:
            connector.logger.debug(e, __name__)

        if result:
            if not self.doi:
                self.doi = result['doi']
            if result['pubType'] == 'preprint':
                self.journal = result['bookOrReportDetails']['publisher']
            else:
                if result['pmid']:
                    self.PMID = result['pmid']
                self.journal = result['journalTitle']
            self.firstauthor = result['authorString'].split(',')[0]
            self.authors = result['authorString']
            self.title = result['title']
            self.date_publication = result['firstPublicationDate']
            return True
        else:
            return False


    def check_data(self, fields_infos, mandatory_fields):
        extra_fields_info = {
            'firstauthor': { 'type': 'string', 'label': 'Remotely fetched first author' },
            'authors': { 'type': 'string', 'label': 'Remotely fetched author' },
            'title': { 'type': 'string', 'label': 'Remotely fetched title' },
            'date_publication' : { 'type': 'string', 'label': 'Remotely fetched publication date' }
        }
        extra_mandatory_fields = ['firstauthor','authors','title','date_publication']

        for field in extra_fields_info:
            fields_infos[field] = extra_fields_info[field]
        for field in extra_mandatory_fields:
            if not field in mandatory_fields:
                mandatory_fields.append(field)

        validator = PublicationValidator(self, fields_infos, mandatory_fields)
        validator.check_not_null()
        validator.check_format()
        return validator.report


class PublicationValidator(GenericValidator):

    def __init__(self, object, fields_types, mandatory_fields, type="Publication"):
        super().__init__(object, fields_types, mandatory_fields, type)
