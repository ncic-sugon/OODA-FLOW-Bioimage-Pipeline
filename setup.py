#
# Copyright (C) 2016-2017 by  Yuan Lufeng
# See license.txt for full license and copyright notice.
#
# Authors: Yuan Lufeng 
#
# setup.py
#
#  Created on: Dec 11th, 2016
#      Author: Yuan Lufeng 
#
##\brief this version can complie the code include cuda, C++, python and cython.
#
NAME="FCDLR-original"
DESCRIPTION = "Fast Cell Division and Lineage Reconstruction pipeline"
LONG_DESCRIPTION = ''
MAINTAINER = 'Yuan Lufeng'
MAINTAINER_EMAIL = 'yuanlufeng@ncic.ac.cn'
URL = 'https://github.com/septicmk/lambdaimage'
LICENSE = 'BSD'
DOWNLOAR_URL = 'https://github.com/septicmk/lambdaimage'



#with open('lambdaimage/__init__.py') as f:
#    for line in f:
#        if line.startswith('__version__'):
#            VERSION = line.strip().split()[-1][1:-1]
#            break
#with open('requirements.txt') as f:
#    REQUIRE = [l.strip() for l in f.readlines() if l]


if __name__ == '__main__':
    import  os
    from os.path import join as pjoin
    import subprocess
    
    from setuptools import find_packages, setup
    from setuptools.extension import Extension
    from setuptools.command.build_ext import build_ext
    import numpy


    def find_in_path(name, path):
        "Find a file in a search path"
        #adapted fom http://code.activestate.com/recipes/52224-find-a-file-given-a-search-path/
        for dir in path.split(os.pathsep):
            binpath = pjoin(dir, name)
            if os.path.exists(binpath):
                return os.path.abspath(binpath)
        return None
    
    
    def locate_cuda():
        """Locate the CUDA environment on the system
        Returns a dict with keys 'home', 'nvcc', 'include', and 'lib64'
        and values giving the absolute path to each directory.
        Starts by looking for the CUDAHOME env variable. If not found, everything
        is based on finding 'nvcc' in the PATH.
        """
    
        # first check if the CUDAHOME env variable is in use
        if 'CUDAHOME' in os.environ:
            home = os.environ['CUDAHOME']
            nvcc = pjoin(home, 'bin', 'nvcc')
        else:
            # otherwise, search the PATH for NVCC
            nvcc = find_in_path('nvcc', os.environ['PATH'])
            if nvcc is None:
                raise EnvironmentError('The nvcc binary could not be '
                    'located in your $PATH. Either add it to your path, or set $CUDAHOME')
            home = os.path.dirname(os.path.dirname(nvcc))
    
        cudaconfig = {'home':home, 'nvcc':nvcc,
                      'include': pjoin(home, 'include'),
                      'lib64': pjoin(home, 'lib64')}
        for k, v in cudaconfig.iteritems():
            if not os.path.exists(v):
                raise EnvironmentError('The CUDA %s path could not be located in %s' % (k, v))
    
        return cudaconfig
    CUDA = locate_cuda()
    
    
    def customize_compiler_for_nvcc(self):
        """inject deep into distutils to customize how the dispatch
        to gcc/nvcc works.
        
        If you subclass UnixCCompiler, it's not trivial to get your subclass
        injected in, and still have the right customizations (i.e.
        distutils.sysconfig.customize_compiler) run on it. So instead of going
        the OO route, I have this. Note, it's kindof like a wierd functional
        subclassing going on."""
        
        # tell the compiler it can processes .cu
        self.src_extensions.append('.cu')
    
        # save references to the default compiler_so and _comple methods
        default_compiler_so = self.compiler_so
        super = self._compile
    
        # now redefine the _compile method. This gets executed for each
        # object but distutils doesn't have the ability to change compilers
        # based on source extension: we add it.
        def _compile(obj, src, ext, cc_args, extra_postargs, pp_opts):
            if os.path.splitext(src)[1] == '.cu':
                # use the cuda for .cu files
                self.set_executable('compiler_so', CUDA['nvcc'])
                # use only a subset of the extra_postargs, which are 1-1 translated
                # from the extra_compile_args in the Extension class
                postargs = extra_postargs['nvcc']
            else:
                postargs = extra_postargs['gcc']
    
            super(obj, src, ext, cc_args, postargs, pp_opts)
            # reset the default compiler_so, which we might have changed for cuda
            self.compiler_so = default_compiler_so
    
        # inject our redefined _compile method into the class
        self._compile = _compile
    
    
    # run the customize_compiler
    class custom_build_ext(build_ext):
        def build_extensions(self):
            customize_compiler_for_nvcc(self.compiler)
            build_ext.build_extensions(self)
    

    extensions =[
        Extension("_tracking_GMM",
            sources=["_tracking_GMM.pyx","TrackingGaussianMixtureModel.cpp","GaussianMixtureModel.cpp","../Utils/parseConfigFile.cpp","responsibilities.cpp","variationalInference.cpp","../external/xmlParser2/xmlParser.cpp","../external/Nathan/tictoc.c","../UtilsCUDA/knnCuda.cu","../UtilsCUDA/GMEMupdateCUDA.cu","../constants.cpp","../temporalLogicalRules/temporalLogicalRules.cpp","../UtilsCUDA/3DEllipticalHaarFeatures/gentleBoost/gentleBoost.cpp","../temporalLogicalRules/trackletCalculation.cpp","cellDivision.cpp","supportFunctionsMain.cpp","../nucleiChSvWshedPBC/hierarchicalSegmentation.cpp","backgroundDetectionInterface.cpp","kdtree.cpp","../backgroundDetection/backgroundClassifier.cpp","../temporalLogicalRules/supervoxel.cpp","../temporalLogicalRules/localGeometricDescriptor.cpp","../Utils/WishartCDF.cpp","../Utils/MultinormalCDF.cpp","../temporalLogicalRules/nuclei.cpp","../temporalLogicalRules/lineageHyperTree.cpp","../temporalLogicalRules/lineage.cpp","../temporalLogicalRules/GaussianMixtureModel_Redux.cpp","../../build/mylib/array.c","../../build/mylib/mylib.c","../../build/mylib/image.c","../../build/mylib/histogram.c","../../build/mylib/region.c","../../build/mylib/MY_TIFF/tiff.io.c","../../build/mylib/MY_TIFF/tiff.image.c","../../build/mylib/water.shed.c","../../build/mylib/connectivity.c","../../build/mylib/cdf.c","../Utils/CSparse.c","../../build/mylib/draw.c","../../build/mylib/level.set.c","../../build/mylib/linear.algebra.c","../../build/mylib/svg.c","../../build/mylib/filters.c","../../build/mylib/paths.c","../../build/mylib/swc.c","../../build/mylib/fct.min.c","../../build/mylib/utilities.c","../../build/mylib/fct.root.c","../../build/mylib/hash.c","../../build/mylib/snake.c","../temporalLogicalRules/knnCUDA/knnCuda.cu","../external/gsl/gamma.c","../external/gsl/psi.c","../external/gsl/trig.c","../external/gsl/math.c","../external/gsl/exp.c","../external/gsl/zeta.c","../external/gsl/elementary.c","../external/gsl/log.c","../external/gsl/infnan.c","../external/gsl/error.c","../external/gsl/stream.c","../temporalLogicalRules/sparseHungarianAlgorithm/sparseHungarianAlgorithm.cpp","../temporalLogicalRules/sparseHungarianAlgorithm/external/munkres-cpp-master/src/munkres.cpp","../temporalLogicalRules/lineageWindowFeatures.cpp","../external/gsl/fdiv.c"],
            #sources=["_tracking_GMM.pyx","TrackingGaussianMixtureModel.cpp","GaussianMixtureModel.cpp","../Utils/parseConfigFile.cpp","responsibilities.cpp","variationalInference.cpp","../external/xmlParser2/xmlParser.cpp","../external/Nathan/tictoc.c","../UtilsCUDA/knnCuda.cu","../UtilsCUDA/GMEMupdateCUDA.cu","../constants.cpp","../temporalLogicalRules/temporalLogicalRules.cpp","../UtilsCUDA/3DEllipticalHaarFeatures/gentleBoost/gentleBoost.cpp","../temporalLogicalRules/trackletCalculation.cpp","cellDivision.cpp","supportFunctionsMain.cpp","../nucleiChSvWshedPBC/hierarchicalSegmentation.cpp","backgroundDetectionInterface.cpp","kdtree.cpp","../backgroundDetection/backgroundClassifier.cpp","../temporalLogicalRules/supervoxel.cpp","../temporalLogicalRules/localGeometricDescriptor.cpp","../Utils/WishartCDF.cpp","../Utils/MultinormalCDF.cpp","../temporalLogicalRules/nuclei.cpp","../temporalLogicalRules/lineageHyperTree.cpp","../temporalLogicalRules/lineage.cpp","../temporalLogicalRules/GaussianMixtureModel_Redux.cpp","../../build2/mylib/array.c","../../build2/mylib/mylib.c","../../build2/mylib/image.c","../../build2/mylib/histogram.c","../../build2/mylib/region.c","../../build2/mylib/MY_TIFF/tiff.io.c","../../build2/mylib/MY_TIFF/tiff.image.c","../../build2/mylib/water.shed.c","../../build2/mylib/connectivity.c","../../build2/mylib/cdf.c","../Utils/CSparse.c","../../build2/mylib/draw.c","../../build2/mylib/level.set.c","../../build2/mylib/linear.algebra.c","../../build2/mylib/svg.c","../../build2/mylib/filters.c","../../build2/mylib/paths.c","../../build2/mylib/swc.c","../../build2/mylib/fct.min.c","../../build2/mylib/utilities.c","../../build2/mylib/fct.root.c","../../build2/mylib/hash.c","../../build2/mylib/snake.c","../temporalLogicalRules/knnCUDA/knnCuda.cu","../external/gsl/gamma.c","../external/gsl/psi.c","../external/gsl/trig.c","../external/gsl/math.c","../external/gsl/exp.c","../external/gsl/zeta.c","../external/gsl/elementary.c","../external/gsl/log.c","../external/gsl/infnan.c","../external/gsl/error.c","../external/gsl/stream.c","../temporalLogicalRules/sparseHungarianAlgorithm/sparseHungarianAlgorithm.cpp","../temporalLogicalRules/sparseHungarianAlgorithm/external/munkres-cpp-master/src/munkres.cpp","../UtilsCUDA/3DEllipticalHaarFeatures/AnnotationEllipsoid.cpp"],
            #sources=["_tracking_GMM.pyx","TrackingGaussianMixtureModel.cpp","GaussianMixtureModel.cpp","../Utils/parseConfigFile.cpp","responsibilities.cpp","variationalInference.cpp","../external/xmlParser2/xmlParser.cpp","../external/Nathan/tictoc.c","../UtilsCUDA/knnCuda.cu","../UtilsCUDA/GMEMupdateCUDA.cu","../constants.cpp","../temporalLogicalRules/temporalLogicalRules.cpp","../UtilsCUDA/3DEllipticalHaarFeatures/EllipticalHaarFeatures.cpp","../UtilsCUDA/3DEllipticalHaarFeatures/EllipticalHaarFeatures.cu","../UtilsCUDA/3DEllipticalHaarFeatures/gentleBoost/gentleBoost.cpp","../temporalLogicalRules/trackletCalculation.cpp","cellDivision.cpp","supportFunctionsMain.cpp","../nucleiChSvWshedPBC/hierarchicalSegmentation.cpp","backgroundDetectionInterface.cpp","kdtree.cpp","../backgroundDetection/backgroundClassifier.cpp","../temporalLogicalRules/supervoxel.cpp","../temporalLogicalRules/localGeometricDescriptor.cpp","../Utils/WishartCDF.cpp","../Utils/MultinormalCDF.cpp","../temporalLogicalRules/nuclei.cpp","../temporalLogicalRules/lineageHyperTree.cpp","../temporalLogicalRules/lineage.cpp","../temporalLogicalRules/GaussianMixtureModel_Redux.cpp","../../build2/mylib/array.c","../../build2/mylib/mylib.c","../../build2/mylib/image.c","../../build2/mylib/histogram.c","../../build2/mylib/region.c","../../build2/mylib/MY_TIFF/tiff.io.c","../../build2/mylib/MY_TIFF/tiff.image.c","../../build2/mylib/water.shed.c","../../build2/mylib/connectivity.c","../../build2/mylib/cdf.c","../Utils/CSparse.c","../../build2/mylib/draw.c","../../build2/mylib/level.set.c","../../build2/mylib/linear.algebra.c","../../build2/mylib/svg.c","../../build2/mylib/filters.c","../../build2/mylib/paths.c","../../build2/mylib/swc.c","../../build2/mylib/fct.min.c","../../build2/mylib/utilities.c","../../build2/mylib/fct.root.c","../../build2/mylib/hash.c","../../build2/mylib/snake.c","../temporalLogicalRules/knnCUDA/knnCuda.cu","../external/gsl/gamma.c","../external/gsl/psi.c","../external/gsl/trig.c","../external/gsl/math.c","../external/gsl/exp.c","../external/gsl/zeta.c","../external/gsl/elementary.c","../external/gsl/log.c","../external/gsl/infnan.c","../external/gsl/error.c","../external/gsl/stream.c","../temporalLogicalRules/sparseHungarianAlgorithm/sparseHungarianAlgorithm.cpp","../temporalLogicalRules/sparseHungarianAlgorithm/external/munkres-cpp-master/src/munkres.cpp","../UtilsCUDA/3DEllipticalHaarFeatures/AnnotationEllipsoid.cpp"],
            #sources=["_tracking_GMM.pyx","TrackingGaussianMixtureModel.cpp","GaussianMixtureModel.cpp","../Utils/parseConfigFile.cpp","responsibilities.cpp","variationalInference.cpp","../external/xmlParser2/xmlParser.cpp","../external/Nathan/tictoc.c","../UtilsCUDA/knnCuda.cu","../UtilsCUDA/GMEMupdateCUDA.cu","../constants.cpp","../temporalLogicalRules/temporalLogicalRules.cpp","../UtilsCUDA/3DEllipticalHaarFeatures/EllipticalHaarFeatures.cu","../UtilsCUDA/3DEllipticalHaarFeatures/gentleBoost/gentleBoost.cpp","../temporalLogicalRules/trackletCalculation.cpp","cellDivision.cpp","supportFunctionsMain.cpp","../nucleiChSvWshedPBC/hierarchicalSegmentation.cpp","backgroundDetectionInterface.cpp","kdtree.cpp","../backgroundDetection/backgroundClassifier.cpp","../temporalLogicalRules/supervoxel.cpp","../temporalLogicalRules/localGeometricDescriptor.cpp","../Utils/WishartCDF.cpp","../Utils/MultinormalCDF.cpp","../temporalLogicalRules/nuclei.cpp","../temporalLogicalRules/lineageHyperTree.cpp","../temporalLogicalRules/GaussianMixtureModel_Redux.cpp","../../build2/mylib/array.c","../../build2/mylib/mylib.c","../../build2/mylib/image.c","../../build2/mylib/histogram.c","../../build2/mylib/region.c","../../build2/mylib/MY_TIFF/tiff.io.c","../../build2/mylib/MY_TIFF/tiff.image.c","../../build2/mylib/water.shed.c","../../build2/mylib/connectivity.c","../../build2/mylib/cdf.c","../Utils/CSparse.c","../../build2/mylib/draw.c","../../build2/mylib/level.set.c","../../build2/mylib/fft.c","../../build2/mylib/linear.algebra.c","../../build2/mylib/svg.c","../../build2/mylib/filters.c","../../build2/mylib/paths.c","../../build2/mylib/swc.c","../../build2/mylib/fct.min.c","../../build2/mylib/utilities.c","../../build2/mylib/fct.root.c","../../build2/mylib/hash.c","../../build2/mylib/snake.c"],
            #sources=["_tracking_GMM.pyx","TrackingGaussianMixtureModel.cpp","GaussianMixtureModel.cpp","../Utils/parseConfigFile.cpp","responsibilities.cpp","variationalInference.cpp","../external/xmlParser2/xmlParser.cpp","../external/Nathan/tictoc.c","../UtilsCUDA/knnCuda.cu","../UtilsCUDA/GMEMupdateCUDA.cu","../constants.cpp","../temporalLogicalRules/temporalLogicalRules.cpp","../UtilsCUDA/3DEllipticalHaarFeatures/EllipticalHaarFeatures.cu","../UtilsCUDA/3DEllipticalHaarFeatures/gentleBoost/gentleBoost.cpp","../temporalLogicalRules/trackletCalculation.cpp","cellDivision.cpp","supportFunctionsMain.cpp","../nucleiChSvWshedPBC/hierarchicalSegmentation.cpp","backgroundDetectionInterface.cpp","kdtree.cpp","../backgroundDetection/backgroundClassifier.cpp","../temporalLogicalRules/supervoxel.cpp","../temporalLogicalRules/localGeometricDescriptor.cpp","../Utils/WishartCDF.cpp","../Utils/MultinormalCDF.cpp","../temporalLogicalRules/nuclei.cpp","../temporalLogicalRules/lineageHyperTree.cpp","../temporalLogicalRules/GaussianMixtureModel_Redux.cpp","../../build2/mylib/array.c","../../build2/mylib/mylib.c","../../build2/mylib/image.c","../../build2/mylib/histogram.c","../../build2/mylib/region.c","../../build2/mylib/MY_TIFF/tiff.io.c","../../build2/mylib/MY_TIFF/tiff.image.c","../../build2/mylib/water.shed.c","../../build2/mylib/connectivity.c","../../build2/mylib/cdf.c","../Utils/CSparse.c","../../build2/mylib/draw.c","../../build2/mylib/level.set.c","../../build2/mylib/fft.c","../../build2/mylib/linear.algebra.c","../../build2/mylib/svg.c","../../build2/mylib/filters.c","../../build2/mylib/paths.c","../../build2/mylib/swc.c","../../build2/mylib/fct.min.c","../../build2/mylib/utilities.c","../../build2/mylib/fct.root.c","../../build2/mylib/hash.c","../../build2/mylib/snake.c","../temporalLogicalRules/mylib/MY_FFT/fft.D.c"],
            #sources=["_tracking_GMM.pyx","TrackingGaussianMixtureModel.cpp","GaussianMixtureModel.cpp","../Utils/parseConfigFile.cpp","responsibilities.cpp","variationalInference.cpp","../external/xmlParser2/xmlParser.cpp","../external/Nathan/tictoc.c","../UtilsCUDA/knnCuda.cu","../UtilsCUDA/GMEMupdateCUDA.cu","../constants.cpp","../temporalLogicalRules/temporalLogicalRules.cpp","../UtilsCUDA/3DEllipticalHaarFeatures/EllipticalHaarFeatures.cu","../UtilsCUDA/3DEllipticalHaarFeatures/gentleBoost/gentleBoost.cpp","../temporalLogicalRules/trackletCalculation.cpp","cellDivision.cpp","supportFunctionsMain.cpp","../nucleiChSvWshedPBC/hierarchicalSegmentation.cpp","backgroundDetectionInterface.cpp","kdtree.cpp","../backgroundDetection/backgroundClassifier.cpp","../temporalLogicalRules/supervoxel.cpp","../temporalLogicalRules/localGeometricDescriptor.cpp","../Utils/WishartCDF.cpp","../Utils/MultinormalCDF.cpp","../temporalLogicalRules/nuclei.cpp","../temporalLogicalRules/lineageHyperTree.cpp","../temporalLogicalRules/GaussianMixtureModel_Redux.cpp","../../build2/mylib/array.c","../../build2/mylib/mylib.c","../../build2/mylib/image.c","../../build2/mylib/histogram.c","../../build2/mylib/region.c","../../build2/mylib/MY_TIFF/tiff.io.c","../../build2/mylib/MY_TIFF/tiff.image.c","../../build2/mylib/water.shed.c","../../build2/mylib/connectivity.c","../../build2/mylib/cdf.c","../Utils/CSparse.c","../../build2/mylib/draw.c","../../build2/mylib/level.set.c","../../build2/mylib/fft.c","../../build2/mylib/linear.algebra.c","../../build2/mylib/svg.c","../../build2/mylib/filters.c","../../build2/mylib/paths.c","../../build2/mylib/swc.c","../../build2/mylib/fct.min.c","../../build2/mylib/utilities.c","../../build2/mylib/fct.root.c","../../build2/mylib/hash.c","../../build2/mylib/snake.c","../temporalLogicalRules/mylib/MY_FFT/fft.D.c","../temporalLogicalRules/mylib/MY_FFT/fft.F.c"],
            #sources=["_tracking_GMM.pyx","TrackingGaussianMixtureModel.cpp","GaussianMixtureModel.cpp","../Utils/parseConfigFile.cpp","responsibilities.cpp","variationalInference.cpp","../../build2/mylib/array.c","../../build2/mylib/mylib.c","../../build2/mylib/utilities.c","../../build2/mylib/image.c","../../build2/mylib/MY_TIFF/tiff.image.c","../../build2/mylib/MY_TIFF/tiff.io.c","../../build2/mylib/linear.algebra.c","selectForeground.cpp","watershedSegmentation.cpp","../temporalLogicalRules/supervoxel.cpp","../constants.cpp","set_union.c","hierarchicalSegmentation.cpp","../temporalLogicalRules/localGeometricDescriptor.cpp","agglomerateClustering.cpp","MedianFilter2D/medianFilter2D.cpp","CUDAmedianFilter2D/medianFilter2D.cu"],
            #sources=["_process_stack.pyx","ProcessStack.cpp","IO.cpp","../Utils/parseConfigFile.cpp","../temporalLogicalRules/mylib/array.p"],
            #sources=["_process_stack.pyx","ProcessStack.cpp","IO.cpp","../Utils/parseConfigFile.cpp","../temporalLogicalRules/supervoxel.cpp"],
            #sources=["_process_stack.pyx","ProcessStack.cpp","IO.cpp","hierarchicalSegmentation.cpp","../Utils/parseConfigFile.cpp","watershedPersistanceAgglomeration.cpp","watershedSegmentation.cpp","agglomerateClustering.cpp"],
            include_dirs=[numpy.get_include(),".","..","../temporalLogicalRules/","../nucleiChSvWshedPBC","../mylib/","../backgroundDetection","../UtilsCUDA/3DEllipticalHaarFeatures","../temporalLogicalRules/mylib/MY_TIFF","../temporalLogicalRules/knnCUDA","../external/gsl/","../temporalLogicalRules/sparseHungarianAlgorithm","../temporalLogicalRules/sparseHungarianAlgorithm/external/munkres-cpp-master/src",CUDA['include']],
            #include_dirs=[numpy.get_include(),".","..","../temporalLogicalRules/","../temporalLogicalRules/mylib/","../temporalLogicalRules/mylib/MY_TIFF","MedianFilter2D",CUDA['include']],
            language="c++",
	    #library_dirs = [CUDA['lib64']],
	    library_dirs = ["../../build/UtilsCUDA/3DEllipticalHaarFeatures",CUDA['lib64']],
	    #libraries = ['cudart'],
	    libraries = ['cudart','cusparse','cuda','ellipticalHaarFeatures'],
	    #libraries = ['cudart','cusparse','cuda'],
	    #libraries = ['cudart','cusparse'],
	    #libraries = ['cudart','cusparse','myfft'],
	    #libraries = ['cudart','cusparse','libmyfft.a'],
	    runtime_library_dirs = [CUDA['lib64']],
	    #extra_compile_args=["-std=c++0x","-pthread"],
	    #extra_link_args=["-std=c++0x","-pthread"]),
	    extra_compile_args={'gcc':["-std=c++0x"],
				'nvcc':['-arch=sm_35', '--ptxas-options=-v', '-c', '--compiler-options', "'-fPIC'"]},
	    extra_link_args=["-std=c++0x"]),
        #Extension("lambdatgmm.nucleiSegmentation._io",
        #    sources=["lambdatgmm/nucleiSegmentation/_io.pyx","lambdatgmm/nucleiSegmentation/IO.cpp"],
        #    #sources=["lambdatgmm/nucleiSegmentation/_io.pyx","lambdatgmm/nucleiSegmentation/IO.h"],
        #    include_dirs=[numpy.get_include()],
        #    language="c++"),
        #Extension("lambdaimage.udf._trans",
        #    sources=["lambdaimage/udf/_trans.pyx","lambdaimage/udf/_trans_c.c"],
        #    include_dirs=[numpy.get_include()]),
        #Extension("lambdaimage.udf._update",
        #    sources=["lambdaimage/udf/_update.pyx", "lambdaimage/udf/_update_c.c"],
        #    include_dirs=[numpy.get_include()]),
        #Extension("lambdaimage.udf._moment",
        #    sources=["lambdaimage/udf/_moment.pyx"],
        #    inlcude_dirs=[numpy.get_include()]),
        #Extension("lambdaimage.udf._intensity",
        #    sources=["lambdaimage/udf/_intensity.pyx"],
        #    include_dirs=[numpy.get_include()]),
        #Extension("lambdaimage.udf._phansalkar",
        #    sources=["lambdaimage/udf/_phansalkar.pyx", "lambdaimage/udf/_phansalkar_c.c"],
        #    include_dirs=[numpy.get_include()]),
    ]
    from Cython.Build import cythonize
    extensions = cythonize(extensions)

    setup(
        name = NAME,
        description = DESCRIPTION,
        long_description = LONG_DESCRIPTION,
        maintainer = MAINTAINER,
        maintainer_email = MAINTAINER_EMAIL,
        url=URL,
        license = LICENSE,
        download_url = DOWNLOAR_URL,
        #version = VERSION,
        classifiers = [
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: C',
            'Programming Language :: C++',
            'Programming Language :: Python',
            'Topic :: Software Development :: Libraries',
            'Topic :: Scientific/Engineering',
            'Topic :: Scientific/Engineering :: Bio-Informatics',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            'Operating System :: Unix',
            'Operating System :: MacOS',
        ],
        #install_requires = REQUIRE,
        packages = find_packages(),
        #cmdclass = {'build_ext': build_ext},
        cmdclass={'build_ext': custom_build_ext},
        ext_modules = extensions
        # since the package has c code, the egg cannot be zipped
      	#zip_safe=False
    )
