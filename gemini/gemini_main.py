#!/usr/bin/env python

import os.path
import sys
import argparse
import textwrap
import gemini_load
import gemini_load_chunk
import gemini_query
import \
    gemini_region, gemini_stats, gemini_dump, \
    gemini_annotate, gemini_windower, \
    gemini_browser, gemini_dbinfo, gemini_merge_chunks, gemini_update
import gemini.version

import tool_compound_hets
import tool_autosomal_recessive
import tool_autosomal_dominant
import tool_de_novo_mutations
import tool_pathways
import tool_lof_sieve
import tool_interactions


def examples(parser, args):

    print
    print "[load] - load a VCF file into a gemini database:"
    print "   gemini load -v my.vcf my.db"
    print "   gemini load -v my.vcf -t snpEff my.db"
    print "   gemini load -v my.vcf -t VEP my.db"
    print

    print "[stats] - report basic statistics about your variants:"
    print "   gemini stats --tstv my.db"
    print "   gemini stats --tstv-coding my.db"
    print "   gemini stats --sfs my.db"
    print "   gemini stats --snp-counts my.db"
    print

    print "[query] - explore the database with ad hoc queries:"
    print "   gemini query -q \"select * from variants where is_lof = 1 and aaf <= 0.01\" my.db"
    print "   gemini query -q \"select chrom, pos, gt_bases.NA12878 from variants\" my.db"
    print "   gemini query -q \"select chrom, pos, in_omim, clin_sigs from variants\" my.db"
    print

    print "[dump] - convenient \"data dumps\":"
    print "   gemini dump --variants my.db"
    print "   gemini dump --genotypes my.db"
    print "   gemini dump --samples my.db"
    print

    print "[region] - access variants in specific genomic regions:"
    print "   gemini region --reg chr1:100-200 my.db"
    print "   gemini region --gene TP53 my.db"
    print

    print "[tools] - there are also many specific tools available"
    print "   1. Find compound heterozygotes."
    print "     gemini comp_hets my.db"
    print

    exit()


def main():

    #########################################
    # create the top-level parser
    #########################################
    parser = argparse.ArgumentParser(prog='gemini')
    parser.add_argument("-v", "--version", help="Installed gemini version",
                        action="version",
                        version="%(prog)s " + str(gemini.version.__version__))
    subparsers = parser.add_subparsers(title='[sub-commands]', dest='command')

    #########################################
    # $ gemini examples
    #########################################
    parser_examples = subparsers.add_parser('examples',
                                            help='show usage examples')
    parser_examples.set_defaults(func=examples)

    #########################################
    # $ gemini load
    #########################################
    parser_load = subparsers.add_parser('load',
                                        help='load a VCF file in gemini database')
    parser_load.add_argument('db', metavar='db',
                             help='The name of the database to be created.')
    parser_load.add_argument('-v', dest='vcf',
                             help='The VCF file to be loaded.')
    parser_load.add_argument('-t', dest='anno_type',
                             default=None, metavar='STRING',
                             help="The annotations to be used with the input vcf. Options are:\n"
                             "  snpEff  - Annotations as reported by snpEff.\n"
                             "  VEP     - Annotations as reported by VEP.\n"
                             )
    parser_load.add_argument('-p', dest='ped_file',
                             help='Sample information file in PED+ format.',
                             default=None)
    parser_load.add_argument('--load-gerp-bp',
                             dest='load_gerp_bp',
                             action='store_true',
                             help='Load GERP scores at base pair resolution. Slow. Off by default.',
                             default=False)
    parser_load.add_argument('--no-load-genotypes',
                             dest='no_load_genotypes',
                             action='store_true',
                             help='Genotypes exist in the file, but should not be stored.',
                             default=False)
    parser_load.add_argument('--no-genotypes',
                             dest='no_genotypes',
                             action='store_true',
                             help='There are no genotypes in the file (e.g. some 1000G VCFs)',
                             default=False)
    parser_load.add_argument('--cores', dest='cores',
                             default=1,
                             type=int,
                             help="Number of cores to use to load in parallel.")
    parser_load.add_argument('--lsf-queue',
                             dest='lsf_queue',
                             help="Queue name to use for Platform LSF.")
    parser_load.add_argument('--sge-queue',
                             dest='sge_queue',
                             help="Queue name to use for Sun Grid Engine.")
    parser_load.add_argument('--torque-queue',
                             dest='torque_queue',
                             help="Queue name to use for a Torque based scheduler")

    parser_load.set_defaults(func=gemini_load.load)

    #########################################
    # $ gemini load_chunk
    #########################################
    parser_loadchunk = subparsers.add_parser('load_chunk',
                                             help='load a VCF file in gemini database')
    parser_loadchunk.add_argument('db',
                                  metavar='db',
                                  help='The name of the database to be created.')
    parser_loadchunk.add_argument('-v',
                                  dest='vcf',
                                  help='The VCF file to be loaded.')
    parser_loadchunk.add_argument('-t',
                                  dest='anno_type',
                                  default=None,
                                  metavar='STRING',
                                  help="The annotations to be used with the input vcf. Options are:\n"
                                  "  snpEff  - Annotations as reported by snpEff.\n"
                                  "  VEP     - Annotations as reported by VEP.\n"
                                  )
    parser_loadchunk.add_argument('-o',
                                  dest='offset',
                                  help='The starting number for the variant_ids',
                                  default=None)
    parser_loadchunk.add_argument('-p',
                                  dest='ped_file',
                                  help='Sample information file in PED+ format.',
                                  default=None)
    parser_loadchunk.add_argument('--no-load-genotypes',
                                  dest='no_load_genotypes',
                                  action='store_true',
                                  help='Genotypes exist in the file, but should not be stored.',
                                  default=False)
    parser_loadchunk.add_argument('--no-genotypes',
                                  dest='no_genotypes',
                                  action='store_true',
                                  help='There are no genotypes in the file (e.g. some 1000G VCFs)',
                                  default=False)
    parser_loadchunk.add_argument('--load-gerp-bp',
                                  dest='load_gerp_bp',
                                  action='store_true',
                                  help='Load GERP scores at base pair resolution. Slow. Off by default.',
                                  default=False)
    parser_loadchunk.set_defaults(func=gemini_load_chunk.load)

    #########################################
    # $ gemini merge_chunks
    #########################################
    parser_mergechunks = subparsers.add_parser('merge_chunks',
            help='combine intermediate db files into the final gemini ')
    parser_mergechunks.add_argument('--db',
            dest='db',
            help='The name of the final database to be loaded.')
    parser_mergechunks.add_argument('--chunkdb',
            nargs='*',
            dest='chunkdbs',
            action='append')

    parser_mergechunks.set_defaults(func=gemini_merge_chunks.merge_chunks)

    #########################################
    # $ gemini query
    #########################################
    parser_query = subparsers.add_parser('query',
            help='issue ad hoc SQL queries to the DB')
    parser_query.add_argument('db',
            metavar='db',
            help='The name of the database to be queried.')
    parser_query.add_argument('-q',
            dest='query',
            metavar='QUERY_STR',
            help='The query to be issued to the database')
    parser_query.add_argument('--gt-filter',
            dest='gt_filter',
            metavar='STRING',
            help='Restrictions to apply to genotype values')
    parser_query.add_argument('--show-samples',
                              dest='show_variant_samples',
                              action='store_true',
                              default=False,
                              help=('Add a column of all sample names with a variant to each '
                                    'variant.'))
    parser_query.add_argument('--header',
            dest='use_header',
            action='store_true',
            help='Add a header of column names to the output.',
            default=False)
    parser_query.set_defaults(func=gemini_query.query)

    #########################################
    # $ gemini dump
    #########################################
    parser_dump = subparsers.add_parser('dump',
            help='shortcuts for extracting data from the DB')
    parser_dump.add_argument('db',
            metavar='db',
            help='The name of the database to be queried.')
    parser_dump.add_argument('--variants',
            dest='variants',
            action='store_true',
            help='Report all rows/columns from the variants table.',
            default=False)
    parser_dump.add_argument('--genotypes',
            dest='genotypes',
            action='store_true',
            help='Report all rows/columns from the variants table \nwith one line per sample/genotype.',
            default=False)
    parser_dump.add_argument('--samples',
            dest='samples',
            action='store_true',
            help='Report all rows/columns from the samples table.',
            default=False)
    parser_dump.add_argument('--header',
            dest='use_header',
            action='store_true',
            help='Add a header of column names to the output.',
            default=False)
    parser_dump.add_argument('--sep',
            dest='separator',
            metavar='STRING',
            help='Output column separator',
            default="\t")
    parser_dump.set_defaults(func=gemini_dump.dump)

    #########################################
    # $ gemini region
    #########################################
    parser_region = subparsers.add_parser('region',
            help='extract variants from specific genomic loci')
    parser_region.add_argument('db',
            metavar='db',
            help='The name of the database to be queried.')
    parser_region.add_argument('--reg',
            dest='region',
            metavar='STRING',
            help='Specify a chromosomal region chr:start-end')
    parser_region.add_argument('--gene',
            dest='gene',
            metavar='STRING',
            help='Specify a gene of interest')
    parser_region.add_argument('--header',
            dest='use_header',
            action='store_true',
            help='Add a header of column names to the output.',
            default=False)
    parser_region.add_argument('--sep',
            dest='separator',
            metavar='STRING',
            help='Output column separator',
            default="\t")
    parser_region.set_defaults(func=gemini_region.region)

    #########################################
    # $ gemini stats
    #########################################
    parser_stats = subparsers.add_parser('stats',
            help='compute useful variant stastics')
    parser_stats.add_argument('db',
            metavar='db',
            help='The name of the database to be queried.')
    parser_stats.add_argument('--tstv',
            dest='tstv',
            action='store_true',
            help='Report the overall ts/tv ratio.',
            default=False)
    parser_stats.add_argument('--tstv-coding',
            dest='tstv_coding',
            action='store_true',
            help='Report the ts/tv ratio in coding regions.',
            default=False)
    parser_stats.add_argument('--tstv-noncoding',
            dest='tstv_noncoding',
            action='store_true',
            help='Report the ts/tv ratio in non-coding regions.',
            default=False)
    parser_stats.add_argument('--snp-counts',
            dest='snp_counts',
            action='store_true',
            help='Report the count of each type of SNP (A->G, G->T, etc.).',
            default=False)
    parser_stats.add_argument('--sfs',
            dest='sfs',
            action='store_true',
            help='Report the site frequency spectrum of the variants.',
            default=False)
    parser_stats.add_argument('--mds',
            dest='mds',
            action='store_true',
            help='Report the pairwise genetic distance between the samples.',
            default=False)
    parser_stats.add_argument('--vars-by-sample',
            dest='variants_by_sample',
            action='store_true',
            help='Report the number of variants observed in each sample.',
            default=False)
    parser_stats.add_argument('--gts-by-sample',
            dest='genotypes_by_sample',
            action='store_true',
            help='Report the count of each genotype class obs. per sample.',
            default=False)
    parser_stats.add_argument('--summarize',
            dest='query',
            metavar='QUERY_STR',
            default=None,
            help='The query to be issued to the database to summarize')
    parser_stats.set_defaults(func=gemini_stats.stats)

    #########################################
    # gemini annotate
    #########################################
    parser_get = subparsers.add_parser('annotate',
            help='Add new columns for custom annotations')
    parser_get.add_argument('db',
            metavar='db',
            help='The name of the database to be updated.')
    parser_get.add_argument('-f',
            dest='anno_file',
            help='The BED file containing the annotations')
    parser_get.add_argument('-c',
            dest='col_name',
            help='The name of the column to be added to the variant table.')
    parser_get.add_argument('-t',
            dest='col_type',
            help='How the data for the new column (-c) should be stored.',
            default="append",
            choices=['boolean', 'count', 'list'])
    parser_get.add_argument('-e',
            dest='col_extract',
            help='Column to extract information from for list annotations.')
    parser_get.set_defaults(func=gemini_annotate.annotate)

    #########################################
    # gemini windower
    #########################################
    parser_get = subparsers.add_parser('windower',
            help='Compute statistics across genome \"windows\"')
    parser_get.add_argument('db',
            metavar='db',
            help='The name of the database to be updated.')
    parser_get.add_argument('-w',
            dest='window_size',
            default=1000000,
            help='The name of the column to be added to the variant table.')
    parser_get.add_argument('-s',
            dest='step_size',
            default=0,
            help="The step size for the windows in bp.\n")
    parser_get.add_argument('-t',
            dest='analysis_type',
            help='The type of windowed analysis requested.',
            choices=['nucl_div', 'hwe'],
            default='hwe')
    parser_get.add_argument('-o',
            dest='op_type',
            help='The operation that should be applied to the -t values.',
            choices=['mean', 'median', 'min', 'max', 'collapse'],
            default='mean')
    parser_get.set_defaults(func=gemini_windower.windower)

    #########################################
    # gemini db_info
    #########################################
    parser_get = subparsers.add_parser('db_info',
            help='Get the names and types of cols. database tables')
    parser_get.add_argument('db',
            metavar='db',
            help='The name of the database to be updated.')
    parser_get.set_defaults(func=gemini_dbinfo.db_info)

    #########################################
    # $ gemini comp_hets
    #########################################
    parser_comp_hets = subparsers.add_parser('comp_hets',
            help='Identify compound heterozygotes')
    parser_comp_hets.add_argument('db',
            metavar='db',
            help='The name of the database to be created.')
    parser_comp_hets.add_argument('--allow-other-hets',
            dest='allow_other_hets',
            action='store_true',
            help='Allow other het. individuals when screening candidates.',
            default=False)
    parser_comp_hets.add_argument('--only_lof',
            dest='only_lof',
            action='store_true',
            help='Only consider variants that are loss of function',
            default=False)
    parser_comp_hets.add_argument('--ignore_phasing',
            dest='ignore_phasing',
            action='store_true',
            help='Ignore phasing when screening for compound hets. \
                  Candidates are inherently _putative_.',
            default=False)
    parser_comp_hets.set_defaults(func=tool_compound_hets.run)

    #########################################
    # $ gemini pathways
    #########################################
    parser_pathway = subparsers.add_parser('pathways',
            help='Map genes and variants to KEGG pathways')
    parser_pathway.add_argument('db',
            metavar='db',
            help='The name of the database to be queried')
    parser_pathway.add_argument('-v',
            dest='version',
            default='68',
            metavar='STRING',
            help="Version of ensembl genes to use. "
                 "Supported versions: 66 to 71\n"
            )
    parser_pathway.add_argument('--lof',
            dest='lof',
            action='store_true',
            help='Report pathways for indivs/genes/sites with LoF variants',
            default=False)
    parser_pathway.set_defaults(func=tool_pathways.pathways)

    #########################################
    # $ gemini lof_sieve
    #########################################
    parser_lof_sieve = subparsers.add_parser('lof_sieve',
            help='Prioritize LoF mutations')
    parser_lof_sieve.add_argument('db',
            metavar='db',
            help='The name of the database to be queried')
    parser_lof_sieve.set_defaults(func=tool_lof_sieve.lof_sieve)

    #########################################
    # $ gemini interactions
    #########################################
    parser_interaction = subparsers.add_parser('interactions',
            help='Find interaction partners for a gene in sample variants(default mode)')
    parser_interaction.add_argument('db',
            metavar='db',
            help='The name of the database to be queried')
    parser_interaction.add_argument('-g',
            dest='gene',
            help='Gene to be used as a root in BFS/shortest_path')
    parser_interaction.add_argument('-r',
            dest='radius',
            type=int,
            help="Set filter for BFS:\n"
                 "valid numbers starting from 0")
    parser_interaction.add_argument('--var',
            dest='var_mode',
            help='var mode: Returns variant info (e.g. impact, biotype) for interacting genes',
            action='store_true',
            default=False)
    parser_interaction.set_defaults(func=tool_interactions.genequery)

    #########################################
    # gemini lof_interactions
    #########################################
    parser_interaction = subparsers.add_parser('lof_interactions',
            help='Find interaction partners for a lof gene in sample variants(default mode)')
    parser_interaction.add_argument('db',
            metavar='db',
            help='The name of the database to be queried')
    parser_interaction.add_argument('-r',
            dest='radius',
            type=int,
            help="set filter for BFS:\n")
    parser_interaction.add_argument('--var',
            dest='var_mode',
            help='var mode: Returns variant info (e.g. impact, biotype) for interacting genes',
            action='store_true',
            default=False)
    parser_interaction.set_defaults(func=tool_interactions.lofgenequery)

    #########################################
    # $ gemini autosomal_recessive
    #########################################
    parser_auto_rec = subparsers.add_parser('autosomal_recessive',
            help='Identify variants meeting an autosomal \
                  recessive inheritance model')
    parser_auto_rec.add_argument('db',
            metavar='db',
            help='The name of the database to be queried.')
    parser_auto_rec.set_defaults(func=tool_autosomal_recessive.run)

    #########################################
    # $ gemini autosomal_dominant
    #########################################
    parser_auto_dom = subparsers.add_parser('autosomal_dominant',
            help='Identify variants meeting an autosomal \
                  dominant inheritance model')
    parser_auto_dom.add_argument('db',
            metavar='db',
            help='The name of the database to be queried.')
    parser_auto_dom.set_defaults(func=tool_autosomal_dominant.run)

    #########################################
    # $ gemini de_novo
    #########################################
    parser_de_novo = subparsers.add_parser('de_novo',
            help='Identify candidate de novo mutations')
    parser_de_novo.add_argument('db',
            metavar='db',
            help='The name of the database to be queried.')
    parser_de_novo.add_argument('-d',
            dest='min_sample_depth',
            type=int,
            help="The minimum aligned\
                  sequence depth (genotype DP) req'd for\
                  each sample",
            default=20)
    parser_de_novo.set_defaults(func=tool_de_novo_mutations.run)

    #########################################
    # $ gemini browser
    #########################################
    parser_browser = subparsers.add_parser('browser',
            help='Browser interface to gemini')
    parser_browser.add_argument('db', metavar='db',
            help='The name of the database to be queried.')
    parser_browser.set_defaults(func=gemini_browser.browser_main)

    #########################################
    # $ gemini update
    #########################################
    parser_update = subparsers.add_parser("update", help="Update gemini software and data files.")
    parser_update.set_defaults(func=gemini_update.release)

    #######################################################
    # parse the args and call the selected function
    #######################################################
    args = parser.parse_args()
    args.func(parser, args)

    # make sure database is found
    if hasattr(args, "db") and args.db is not None and not os.path.exists(args.db):
        sys.stderr.write("Requested GEMINI database (%s) not found. "
                         "Please confirm the provided filename.\n" % args.db)

if __name__ == "__main__":
    main()
