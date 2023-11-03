import sql_utils as su
import gpt_utils as gu
import time


def database_structure_strings():

    NanoEntDes_structure = "{table:NanoEntDes,attributes:" + \
        "[ID(Primary),NanoEntity,Description]}"

    NanoEntCom_structure = "{table:NanoEntCom,attributes:" + \
        "[ID(Primary),NanoEntity,Composition,CompositionType," + \
        "MolecularWeight,PubChemID]}"

    FuncEntDes_structure = "{table: FuncEntDes, attributes:" + \
        "[ID(Primary),FunctionEntity,FunctionEntityType," + \
        "Description,ActivationMethod,pubChemID," + \
        "MolarMass,MolarMassUnit]}"

    FuncEntFunction_structure = "{table: FuncEntFunction," + \
        "attributes:[ID(Primary),FunctionEntiry,Function," + \
        "FunctionDescription]}"

    ChemAsso_structure = "{table: ChemAsso, attributes:" + \
        "[ID(Primary),AssociationType,BondType,Description," + \
        "dataId,ComposingElementNameA,ComposingElementNameB," + \
        "CompositiontypeB,CompositiontypeA,DomainElementNameB," + \
        "DomainElementNameA,DomainAssociationId,ComposingElemetIdB," + \
        "ComposingElemetIdA,ComposingElementTypeA,EntityDisplayNameB," + \
        "ComposingElementTypeB,EntityDisplayNameA,AttachmentId}"

    GeneralInfo_structure = "{table:GeneralInfo,attributes:" + \
        "[ID(Primary),sampleName,createdYear,createdMonth]}"

    SampleKeywords_structure = "{table:SampleKeyWords,attributes:" + \
        "[ID(Primary),sampleName,SampleKeyWord]}"

    PublicationInfo_structure = "{table:PublicationInfo," + \
        "attributes:[ID(Primary),PMID,year,title,author," + \
        "journal,publicationCategories,description]}"

    PublicationKeyWords_structure = "{table:PublicationKeyWords," + \
        "attributes:[ID(Primary),sampleName,SampleKeyWord]}"

    CharacterizationInfo_structure = "{table:CharacterizationInfo," + \
        "attributes:[ID(Primary),CharType,CharName," + \
        "AssayType,Protocol, " + \
        "DesignDescription,AnalysisAndConclusion]}"

    CharExpConfig_structure = "{table:CharExpConfig," + \
        "attributes:[ID(Primary),CharType,CharName," + \
        "AssayType,ExpConfigTechnique, " + \
        "ExpConfigInstruments,ExpConfigDescription]}"

    CharResultDescriptions_structure = "{table:CharResultDescriptions," + \
        "attributes:[ID(Primary),CharType,CharName," + \
        "AssayType,CharResultDescription]}"

    CharResultKeywords_structure = "{table:CharResultKeywords," + \
        "attributes:[ID(Primary),CharType,CharName," + \
        "AssayType,CharResultKeyword]}"

    CharResultTables_structure = "{table:CharResultTables," + \
        "attributes:[ID(Primary),CharType,CharName," + \
        "AssayType,CharTable]}"

    note1 = "NanoEntCom should not be used to count unique " + \
        "NanoEntity\ncount composition should only use composition table"

    note2 = "ALL tables shoud join on ID. Table NanoEntDes and " + \
        "NanoEntCom share key NanoEntity, " + \
        "FuncEntDes and FuncEntFunction share FunctionEntity key, " + \
        "ChemAsso does not have other common keys with other tables."

    note3 = "Strictly reference to table name and columns in this context. "

    Overall_structure = [
        "\n",
        NanoEntDes_structure,
        NanoEntCom_structure,
        FuncEntDes_structure,
        FuncEntFunction_structure,
        ChemAsso_structure,
        GeneralInfo_structure,
        SampleKeywords_structure,
        PublicationInfo_structure,
        PublicationKeyWords_structure,
        CharacterizationInfo_structure,
        CharExpConfig_structure,
        CharResultDescriptions_structure,
        CharResultKeywords_structure,
        CharResultTables_structure,
        note1,
        note2,
        note3
    ]

    Overall_structure_string = "\n".join(Overall_structure)

    return Overall_structure_string


def custom_query(
    question,
    connection,
    GPT4=True,
    print_prompt=False,
    print_token=False,
    print_query=False,
    print_time=False
):

    stucture = database_structure_strings()

    context_token_count = gu.num_tokens_from_string(
        stucture
    )

    prompt = su.sql_prompt(
        question,
        stucture
    )

    prompt_token_count = gu.num_tokens_from_string(prompt)

    if print_prompt:
        print(prompt)

    if print_token:
        print(f"\nContext token count: {context_token_count}")
        print(f"Prompt token count: {prompt_token_count}")

    start_time = time.time()

    if GPT4:
        query = gu.quick_ask(prompt, model_num=0)
    else:
        query = gu.quick_ask(prompt, model_num=1)

    if print_query:
        print("\n============= The Query is: ===============\n")
        print(query)
        print("\n===========================================\n")

    result_df = su.submit_querry(query, connection)
    # End the timer
    end_time = time.time()
    # Calculate the execution time
    execution_time = end_time - start_time
    # Print the execution time
    if print_time:
        print("\nExecution Time:", execution_time, "seconds")

    return result_df, query
