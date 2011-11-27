# maven-release parent pom version
%global pversion 16
# maven-release-manager jar version
%global mjarver 2.0
# maven-release-plugin jar version
%global pjarver 2.0

Name:           maven-release
Version:        2.0
Release:        5
Summary:        Release a project updating the POM and tagging in the SCM

Group:          Development/Java
License:        ASL 2.0
URL:            http://maven.apache.org/plugins/maven-release-plugin/
# tar creation instructions
# svn export http://svn.apache.org/repos/asf//maven/release/tags/maven-release-2.0 maven-release-2.0
# tar cfJ maven-release-2.0.tar.xz maven-release-2.0 
Source0:        maven-release-2.0.tar.xz
Source1:        maven-release-jpp-depmap.xml
# Remove jmock needed for tests and set source to 1.4 to support assert stmt
Patch0:         001_mavenreleasemanager_fixbuild.patch
# Remove deps needed for tests, till jmock gets packaged
Patch1:         002_mavenreleaseplugin_skiptests.patch
BuildArch:      noarch

BuildRequires:  java-devel
BuildRequires:  jpackage-utils
BuildRequires:  maven-scm >= 1.4-1
BuildRequires:  maven-scm-test >= 1.4-1
BuildRequires:  maven2
BuildRequires:  maven2-common-poms >= 0:1.0-13
BuildRequires:  maven-antrun-plugin
BuildRequires:  maven-jar-plugin
BuildRequires:  maven-javadoc-plugin
BuildRequires:  maven-source-plugin
BuildRequires:  maven-compiler-plugin
BuildRequires:  maven-install-plugin
BuildRequires:  maven-plugin-plugin
BuildRequires:  maven-resources-plugin
BuildRequires:  maven-site-plugin
BuildRequires:  maven-plugin-testing-harness
BuildRequires:  plexus-maven-plugin
BuildRequires:  plexus-utils
BuildRequires:  maven-surefire-maven-plugin
BuildRequires:  jaxen

Requires:       java 
Requires:       jpackage-utils

Requires(post):   jpackage-utils
Requires(postun): jpackage-utils


%description
This plugin is used to release a project with Maven, saving a lot of 
repetitive, manual work. Releasing a project is made in two steps: 
prepare and perform.


%package manager
Summary:        Release a project updating the POM and tagging in the SCM
Group:          Development/Java
Requires:       %{name} = %{version}-%{release}
Requires:       jpackage-utils
BuildArch:      noarch

%description manager
This package contains %{name}-manager needed by %{name}-plugin.


%package plugin
Summary:        Release a project updating the POM and tagging in the SCM
Group:          Development/Java
Requires:       %{name}-manager = %{version}-%{release}
Requires:       jpackage-utils
BuildArch:      noarch

%description plugin
This plugin is used to release a project with Maven, saving a lot of
repetitive, manual work. Releasing a project is made in two steps:
prepare and perform.


%package javadoc
Summary:        Javadocs for %{name}
Group:          Development/Java
Requires:       %{name} = %{version}-%{release}
Requires:       jpackage-utils
Obsoletes:      %{name}-manager-javadoc <= 2.0-1
Obsoletes:      %{name}-plugin-javadoc <= 2.0-1
BuildArch:      noarch

%description javadoc
This package contains the API documentation for %{name}.


%prep
%setup -q -n %{name}-%{version}
%patch0 -p1
%patch1 -p1
cat > README << EOT
%{name}-%{version}

This plugin is used to release a project with Maven, saving a lot of
repetitive, manual work. Releasing a project is made in two steps:
prepare and perform.
EOT


%build
export MAVEN_REPO_LOCAL=$(pwd)/.m2/repository
mkdir -p $MAVEN_REPO_LOCAL

mvn-jpp \
  -e  \
  -Dmaven.repo.local=$MAVEN_REPO_LOCAL \
  -Dmaven2.jpp.depmap.file=%{SOURCE1} \
  -Dmaven.test.skip=true \
  install javadoc:aggregate


%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT%{_javadir}

# jars
install -Dp -m 644 %{name}-manager/target/%{name}-manager-%{mjarver}.jar \
  $RPM_BUILD_ROOT%{_javadir}//%{name}-manager.jar

install -Dp -m 644 %{name}-plugin/target/%{name}-plugin-%{pjarver}.jar \
  $RPM_BUILD_ROOT%{_javadir}/%{name}-plugin.jar

# javadocs
mkdir -p $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -rp target/site/apidocs/  \
  $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
(cd $RPM_BUILD_ROOT%{_javadocdir} && ln -sf %{name}-%{version} %{name})

# poms
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/maven2/poms
install -pm 644 pom.xml  \
  $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP-%{name}.pom
install -pm 644 %{name}-manager/pom.xml  \
  $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP-%{name}-manager.pom
install -pm 644 %{name}-plugin/pom.xml  \
  $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP-%{name}-plugin.pom

%add_to_maven_depmap org.apache.maven.release %{name} %{pversion} JPP %{name}
%add_to_maven_depmap org.apache.maven.release %{name}-manager %{mjarver} JPP %{name}-manager
%add_to_maven_depmap org.apache.maven.plugins %{name}-plugin %{pjarver} JPP %{name}-plugin

%files
%defattr(-,root,root,-)
%doc README
%{_mavenpomdir}/JPP-%{name}.pom
%{_mavendepmapfragdir}/*


%files manager
%defattr(-,root,root,-)
%{_javadir}/*manager*
%{_mavenpomdir}/JPP-%{name}-manager.pom


%files plugin
%defattr(-,root,root,-)
%{_javadir}/*plugin*
%{_mavenpomdir}/JPP-%{name}-plugin.pom


%files javadoc
%defattr(-,root,root,-)
%{_javadocdir}/%{name}
%{_javadocdir}/%{name}-%{version}


%post
%update_maven_depmap


%postun
%update_maven_depmap


