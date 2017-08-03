import glob
import mock
import os
import sys
import unittest
import uuid

import msi_profiler
from models import MicroSatelliteProfiler


class MSIProfilerTests(unittest.TestCase):
    TEST_DIR = "test-data"
    TUMOR_BAM_PATH = TEST_DIR
    NORMAL_BAM_PATH = TEST_DIR
    GOOD_PHASED = "{}/good_phased.txt".format(TEST_DIR)
    GOOD_UNPHASED = "{}/good_unphased.txt".format(TEST_DIR)
    GOOD_PHASED_MULTICORE = "{}/good_phased_multi.txt".format(TEST_DIR)
    GOOD_UNPHASED_MULTICORE = "{}/good_unphased_multi.txt".format(TEST_DIR)
    OUTPUT_PREFIX = "{}_test".format(str(uuid.uuid4()))
    OUTPUT_PREFIX_MULTICORE = OUTPUT_PREFIX + "_multicore"
    MULTI_PROC = 2
    SINGLE_PROC = 1

    def setUp(self):
        self.mode = MicroSatelliteProfiler.PHASED

        self.TEST_ARGS = [
            "python",
            "msi_profiler.py",
            "--tumor_bam",
            "{}/test_tumor.bam".format(self.TUMOR_BAM_PATH),
            "--normal_bam",
            "{}/test_normal.bam".format(self.NORMAL_BAM_PATH),
            "--bed",
            "{}/germline_calls_22_sel1k.bed".format(self.TEST_DIR),
            "--chromosomes",
            "22",
            "--fasta",
            "{}/chrs_fa/".format(self.TEST_DIR),
            "--reference_set",
            "{}/reference_set_22_sorted_test.txt".format(self.TEST_DIR),
            "--min_coverage",
            "5",
            "--min_MS_length",
            "6",
            "--flank_size",
            "5",
            "--rus",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6"
        ]

    def tearDown(self):
        # Remove any test files we've created
        for file_path in glob.glob("./{}*.txt".format(self.OUTPUT_PREFIX)):
            os.remove(file_path)

    def create_micro_satellite_profiler_args(self):
        self.TEST_ARGS.pop(0)
        sys.argv = []
        sys.argv.extend(self.TEST_ARGS)
        parser = msi_profiler.initialize_parser()
        args = parser.parse_args()
        return args

    def run_msiprofiler(self,
                        number_or_processors,
                        output_prefix=OUTPUT_PREFIX):
        self.TEST_ARGS.extend(
            [
                "--mode",
                "{}".format(self.mode),
                "--nprocs",
                "{}".format(number_or_processors),
                "--output_prefix",
                "{}".format(output_prefix),
            ]
        )
        self.TEST_ARGS.pop(0)
        self.TEST_ARGS.pop(0)
        sys.argv.extend(self.TEST_ARGS)
        msi_profiler.main()

    def test_msi_profiler_no_args(self):
        with self.assertRaises(AttributeError):
            MicroSatelliteProfiler({})

    @mock.patch.object(MicroSatelliteProfiler, "_check_processors")
    @mock.patch.object(MicroSatelliteProfiler, "_check_repeat_units")
    @mock.patch.object(MicroSatelliteProfiler, "_check_chromosomes")
    @mock.patch.object(MicroSatelliteProfiler, "_check_mode")
    @mock.patch.object(MicroSatelliteProfiler, "_check_bams")
    @mock.patch.object(MicroSatelliteProfiler, "_check_reference_set")
    @mock.patch.object(MicroSatelliteProfiler, "_check_bed_filename")
    @mock.patch.object(MicroSatelliteProfiler, "_check_fasta_filename")
    @mock.patch.object(MicroSatelliteProfiler, "run")
    def test_proper_arg_validations_are_called(
        self,
        run_mock,
        check_fasta_mock,
        check_bed_mock,
        check_reference_mock,
        check_bams_mock,
        check_mode_mock,
        check_chromosomes_mock,
        check_repeat_units_mock,
        check_processors_mock
    ):
        self.mode = MicroSatelliteProfiler.PHASED

        self.run_msiprofiler(self.SINGLE_PROC)

        self.assertTrue(run_mock.called)
        self.assertTrue(check_fasta_mock.called)
        self.assertTrue(check_bed_mock.called)
        self.assertTrue(check_reference_mock.called)
        self.assertTrue(check_bams_mock.called)
        self.assertTrue(check_mode_mock.called)
        self.assertTrue(check_chromosomes_mock.called)
        self.assertTrue(check_repeat_units_mock.called)
        self.assertTrue(check_processors_mock.called)

    def test_phased(self):
        self.mode = MicroSatelliteProfiler.PHASED
        self.output_file = "{}_{}.txt".format(self.OUTPUT_PREFIX, self.mode)

        self.run_msiprofiler(self.SINGLE_PROC)

        with open(self.output_file) as test_out,\
                open(self.GOOD_PHASED) as known_good:
            self.assertEqual(known_good.read(), test_out.read())

    def test_unphased(self):
        self.mode = MicroSatelliteProfiler.UNPHASED
        self.output_file = "{}_{}.txt".format(self.OUTPUT_PREFIX, self.mode)

        self.run_msiprofiler(self.SINGLE_PROC)

        with open(self.output_file) as test_out, \
                open(self.GOOD_UNPHASED) as known_good:
            self.assertEqual(known_good.read(), test_out.read())

    def test_multicore_phased(self):
        self.mode = MicroSatelliteProfiler.PHASED
        self.output_file = "{}_{}.txt".format(
            self.OUTPUT_PREFIX_MULTICORE,
            self.mode
        )

        self.run_msiprofiler(
            self.MULTI_PROC,
            output_prefix=self.OUTPUT_PREFIX_MULTICORE
        )

        with open(self.output_file) as test_out, \
                open(self.GOOD_PHASED_MULTICORE) as known_good:
            self.assertEqual(known_good.read(), test_out.read())

    # def test_multicore_unphased(self):
    #     self.output_prefix = "test_multicore"
    #     self.mode = MicroSatelliteProfiler.UNPHASED
    #     self.output_file = "{}_{}.txt".format(
    #           self.OUTPUT_PREFIX_MULTICORE,
    #           self.mode
    # )
    #
    #       self.run_msiprofiler(
    #           self.MULTI_PROC,
    #           output_prefix=self.OUTPUT_PREFIX_MULTICORE
    #       )
    #
    #     with open(self.output_file) as test_out, \
    #             open(self.GOOD_UNPHASED_MULTICORE) as known_good:
    #         self.assertEqual(known_good.read(), test_out.read())

    def test_is_phased(self):
        self.TEST_ARGS.extend(
            [
                "--mode",
                "{}".format(self.mode),
                "--nprocs",
                "{}".format(self.SINGLE_PROC),
                "--output_prefix",
                "{}".format(self.OUTPUT_PREFIX),
            ]
        )

        msp = MicroSatelliteProfiler(
            self.create_micro_satellite_profiler_args()
        )

        self.assertTrue(msp.is_phased)
        self.assertFalse(msp.is_unphased)

    def test_is_unphased(self):
        self.mode = MicroSatelliteProfiler.UNPHASED

        self.TEST_ARGS.extend(
            [
                "--mode",
                "{}".format(self.mode),
                "--nprocs",
                "{}".format(self.SINGLE_PROC),
                "--output_prefix",
                "{}".format(self.OUTPUT_PREFIX),
            ]
        )

        msp = MicroSatelliteProfiler(
            self.create_micro_satellite_profiler_args()
        )
        self.assertTrue(msp.is_unphased)
        self.assertFalse(msp.is_phased)

    def test_bad_tumor_bam_path_raises_proper_exceptions(self):
        self.TUMOR_BAM_PATH = "This path doesn't exit"
        self.setUp()
        self.TEST_ARGS.extend(
            [
                "--mode",
                "{}".format(self.mode),
                "--nprocs",
                "{}".format(self.SINGLE_PROC),
                "--output_prefix",
                "{}".format(self.OUTPUT_PREFIX),
            ]
        )

        with self.assertRaises(RuntimeError) as context:
            MicroSatelliteProfiler(
                self.create_micro_satellite_profiler_args()
            )
        self.assertEqual(
            context.exception.message,
            MicroSatelliteProfiler.TUMOR_BAM_ERROR_MESSAGE
        )

    def test_bad_normal_bam_path_raises_proper_exceptions(self):
        self.NORMAL_BAM_PATH = "This path doesn't exit"
        self.setUp()
        self.TEST_ARGS.extend(
            [
                "--mode",
                "{}".format(self.mode),
                "--nprocs",
                "{}".format(self.SINGLE_PROC),
                "--output_prefix",
                "{}".format(self.OUTPUT_PREFIX),
            ]
        )

        with self.assertRaises(RuntimeError) as context:
            MicroSatelliteProfiler(
                self.create_micro_satellite_profiler_args()
            )
        self.assertEqual(
            context.exception.message,
            MicroSatelliteProfiler.NORMAL_BAM_ERROR_MESSAGE
        )


if __name__ == '__main__':
    unittest.main()