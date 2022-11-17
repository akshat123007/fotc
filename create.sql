CREATE TABLE IF NOT EXISTS public.users  (
    id serial PRIMARY KEY,
    fullname VARCHAR(255) NOT NULL,
    username VARCHAR(50) NOT NULL,
    userpass VARCHAR(255) NOT NULL,
    email VARCHAR(50) NOT NULL, 
    phone VARCHAR(12) NOT NULL
);

CREATE TABLE IF NOT EXISTS public.features  (
    id serial PRIMARY KEY,
    property VARCHAR(255) NOT NULL,
    latitude NUMERIC NOT NULL,
    longitude NUMERIC NOT NULL,
    fullname VARCHAR(50) NOT NULL,
    featurename VARCHAR(255) NOT NULL,
    images VARCHAR(100) NOT NULL, 
    u_id INTEGER REFERENCES public.users (id)  
);