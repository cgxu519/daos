#!/usr/bin/python
"""
  (C) Copyright 2018 Intel Corporation.

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

  GOVERNMENT LICENSE RIGHTS-OPEN SOURCE SOFTWARE
  The Government's rights to use, modify, reproduce, release, perform, display,
  or disclose this software are subject to the terms of the Apache License as
  provided in Contract No. B609815.
  Any reproduction of computer software, computer software documentation, or
  portions thereof marked with this legend must also reproduce the markings.
"""
import numpy as np
from mpi4py import MPI

class DaosFile(object):
    """ Daos I/O is at the research stage, this class provides an abstract
        interface that hides the underlying details and just does some simple
        I/O for building test cases.

        This runs only with a customized DAOS mpich and mpi4py version.
    """

    # just what I need for now
    MODE_RDWR_CREATE = MPI.MODE_RDWR | MPI.MODE_CREATE

    def __init__(self):
        """ setup MPI and some constants in the constructor """
        self.comm = MPI.COMM_WORLD
        self.mpifile = None

    @classmethod
    def open(cls, filename, mode):
        """ Open a DAOS file """
        df = DaosFile()
        fn = "daos:" + filename
        # this uses an environment variable DAOS_POOL to determine
        # where this actually gets written
        df.mpifile = MPI.File.Open(df.comm, fn, mode)
        return df

    def write(self, np_array):
        """ write data from a numpy array into the file """
        self.mpifile.Write(np_array)

    def write_at(self, offset, np_array):
        """ write data from a numpy array into the file """
        self.mpifile.Write_at(offset, np_array)

    def read(self, np_array):
        """ read data into a numpy array """
        self.mpifile.Read(np_array)

    def read_at(self, offset, np_array):
        """ read data into a numpy array """
        self.mpifile.Read_at(offset, np_array)

    def close(self):
        """ done with the file """
        self.mpifile.Close()

if __name__ == "__main__":
    """ this is a unit test driver for this code """

    # create some data to write, integers 0,1,2,...
    # rolling over at 256 and starting over
    data = np.arange(90000000, dtype=np.uint8)

    # create a file
    fh = DaosFile.open("testfile", DaosFile.MODE_RDWR_CREATE)

    # dump some data into it and close
    fh.write(data)
    fh.close()

    # reopen and read data back
    fh = DaosFile.open("testfile", DaosFile.MODE_RDWR_CREATE)
    rdata = np.zeros(1, dtype=np.uint8)
    fh.read_at(89000000,rdata)

    # double check a couple values
    if not rdata == (89000000 % 256):
        print "expecting {0} but value is {1}".format((89000000 % 256), rdata)

    fh.close()
