# FROM nvidia/cuda:11.3.0-devel-ubuntu20.04
# ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
# ENV PATH /opt/conda/bin:$PATH

# # Install Dependencies of Miniconda
# RUN apt-get update --fix-missing && \
#     apt-get install -y wget bzip2 curl git && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

# # Install miniconda3
# RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -O ~/miniconda.sh && \
#     /bin/bash ~/miniconda.sh -b -p /opt/conda && \
#     rm ~/miniconda.sh && \
#     /opt/conda/bin/conda clean --all -y && \
#     ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
#     echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
#     echo "conda activate my_env" >> ~/.bashrc \
#     echo "conda info --envs"

# COPY ./requirements.txt /app/requirements.txt
# RUN /bin/bash -c "conda create --name my_env && source activate my_env && pip install  --file /app/packagelist.txt" 

# CMD [ "/bin/bash" ]

FROM python:3.10

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000