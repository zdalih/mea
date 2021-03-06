import logging, os, json
from .recommend import SimilarUsers
from .curator_movies import CuratorMovies

from django.http import HttpResponse
from .models import LandingPageUser, Movie, Profile
from rest_framework import views
from django.db.utils import IntegrityError
from django.views.generic import View
from django.conf import settings
from django.template import RequestContext

#user creation and login related tools
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.contrib.auth import login as login_user
from django.contrib.auth import logout as logout_user

from imdbpie import Imdb

# class GenerateTokensView(views.APIView):

#     def post(self, request, *args, **kwargs):
#         for user in User.objects.all():
#             Token.objects.get_or_create(user=user)

#         return HttpResponse("Done.", status = 200)

class SignUpView(views.APIView):

    # Create new user and add to LandingPageUser model

    def post(self, request, *args, **kwargs):
        content = request.data
        
        try:
            data = content['email']
        except KeyError:
            return HttpResponse('Email not found.', status=400)

        user = LandingPageUser(email=data)

        try:
        	user.save()
        except IntegrityError:
        	return HttpResponse('User already added!', status=201)
        
        return HttpResponse(status=201)

      
class SignUpView2(views.APIView):
    """
    Create a new user, requires an e-mail, username, and password
    """
    def post(self, request, *args, **kwargs):
        content = request.data

        try:
            email = content['email']
            username = content['username']
            password = content['password']
            firstName = content['firstName']
            lastName = content['lastName']
        except KeyError:
            return HttpResponse('Error in information format', status = 400)

        try:
            user = User.objects.create_user(username, email, password)
            user.first_name = firstName
            user.last_name = lastName

            picurl = "https://picsum.photos/200/300/?random"
            r = requests.get(picurl).url
            user.profile.pic = r
            user.profile.save()
            user.save()
        
        except Exception as e:
            print(e)
            return HttpResponse("User alredy exists.", status=200)

        response = HttpResponse()
        response['token'] = str(user.auth_token)
        response.status_code = 201
        
        return response


class LogoutView(views.APIView):
    """
    logout the user
    """

    def get(self, request, format=None):
        
        request.user.auth_token.delete()

        return HttpResponse(status=200)

        
class ProfileView(views.APIView):
    """
    returns the profile information for the current user
    """

    def get(self, request, *arg, **kwargs):
        current_user = request.user

        print(current_user)

        if current_user.is_authenticated:
            data = {}
            data['username'] = current_user.username
            data['id'] = current_user.profile.id
            data['bio'] = current_user.profile.bio
            data['movies'] = []
            data['followers'] = []
            data['followings'] = []
            data['recommendations'] = []
            data['pictureUrl'] = current_user.profile.pic
            #data['picture'] = current_user.profile.profilePicture
            #PROFILE PICTURE IS TO DO
            user_movies = current_user.profile.movies.all()
            #add in the data dictionary under movies a list
            #of all the movies
            index = 0
            for m in user_movies:
                m_dict = {}
                m_dict['imdbId'] = m.imdbId
                m_dict['title'] = m.title
                m_dict['posterUrl'] = m.poster
                m_dict['year'] = m.year
                m_dict['genres'] = m.genre
                data['movies'].append(m_dict)


            user_followers = current_user.profile.followers.all()
            user_followings = current_user.profile.followings.all()

            for f in user_followers:
                f_dict = {}
                f_dict['username'] = f.user.username
                f_dict['id'] = f.id
                f_dict['pictureUrl'] = f.pic
                data['followers'].append(f_dict)

            for f in user_followings:
                f_dict = {}
                f_dict['username'] = f.user.username
                f_dict['id'] = f.id
                f_dict['pictureUrl'] = f.pic
                data['followings'].append(f_dict)

            user_recommended_movies = current_user.profile.recommended_movies.all()

            for m in user_recommended_movies:
                m_dict = {}
                m_dict['imdbId'] = m.imdbId
                m_dict['title'] = m.title
                m_dict['posterUrl'] = m.poster
                m_dict['year'] = m.year
                m_dict['genres'] = m.genre
                data['recommendations'].append(m_dict)

            profileID = current_user.profile.id
            data['recommendations'].extend(CuratorMovies.get(profileID))

            return HttpResponse(json.dumps(data))

            #data['followers'] = current_user.profile.followerz.all()
            #data['followings'] = current_user.profile.followingz.all()
            #TODO

        else:
            return HttpResponse("No user logged-in.", status = 401)


class PublicProfileView(views.APIView):


    def get(self, request, *arg, **kwargs):

        profileId = kwargs['id'];

        if Profile.objects.filter(id = profileId).exists():
            current_profile = Profile.objects.get(id = profileId)
            data = {}
            data['username'] = current_profile.user.username
            data['id'] = current_profile.id
            data['bio'] = current_profile.bio
            data['pictureUrl'] = current_profile.pic
            data['recommendations'] = []
            data['movies'] = []
            data['followers'] = []
            data['followings'] = []
            #data['picture'] = current_user.profile.profilePicture
            #PROFILE PICTURE IS TO DO

            user_movies = current_profile.movies.all()
            user_recommended_movies = current_profile.recommended_movies.all()

            #add in the data dictionary under movies a list
            #of all the movies
            index = 0

            for m in user_movies:
                m_dict = {}
                m_dict['imdbId'] = m.imdbId
                m_dict['title'] = m.title
                m_dict['posterUrl'] = m.poster
                m_dict['year'] = m.year
                m_dict['genres'] = m.genre
                data['movies'].append(m_dict)

            for m in user_recommended_movies:
                m_dict = {}
                m_dict['imdbId'] = m.imdbId
                m_dict['title'] = m.title
                m_dict['posterUrl'] = m.poster
                m_dict['year'] = m.year
                m_dict['genres'] = m.genre
                data['recommendations'].append(m_dict)

            user_followers = current_profile.followers.all()
            user_followings = current_profile.followings.all()

            for f in user_followers:
                f_dict = {}
                f_dict['username'] = f.user.username
                f_dict['id'] = f.id
                f_dict['pictureUrl'] = f.pic
                data['followers'].append(f_dict)

            for f in user_followings:
                f_dict = {}
                f_dict['username'] = f.user.username
                f_dict['id'] = f.id
                f_dict['pictureUrl'] = f.pic
                data['followings'].append(f_dict)

            return HttpResponse(json.dumps(data))
        else:
            return HttpResponse('No profile found.', status = 404)


class ProfileUpdateView(views.APIView):

    """
    updates user profile information such as bio, add or remove movies,
    or update the profile picture
    """
    def post(self, request, *arg, **kwargs):
        content = request.data
        current_user = request.user

        if current_user.is_authenticated:
            #if key is no present - no need to update
            changeMade = False
            try:
                newBio = content['bio']
                current_user.profile.bio = newBio
                changeMade = True
            except KeyError:
                pass

            try:
                pictureUrl = content['profile_image']
                #TODO
            except KeyError:
                pass

            try:
                movies = content['addMovies']

                for m in movies:
                    if not Movie.objects.filter(imdbId = m['imdbId']).exists():
                        AddMovieToDB(m['imdbId'])

                    movieObject = Movie.objects.get(imdbId = m['imdbId'])
                    current_user.profile.movies.add(movieObject)
                    changeMade = True

            except KeyError:
                pass
            except ValueError:
                return HttpResponse("Invalid movie objects.", status = 400)

            try:
                followsToAdd = content['addFollowings']
                for f in followsToAdd:
                    if Profile.objects.filter(id = f).exists():
                        profile_f = Profile.objects.get(id = f)
                        current_user.profile.followings.add(profile_f)
                        profile_f.followers.add(current_user.profile)
                        changeMade = True
            except KeyError:
                pass
            except ValueError:
                return HttpResponse("User to add does not exist", status = 404)

            try:
                toRemove = content['remove_movie']
                movieObject = Movie.objects.get(imdbId = toRemove)
                current_user.profile.movies.remove(movieObject)
                changeMade = True
            except KeyError:
                pass
            except ValueError:
                return HttpResponse("Movie requested for removal is not on user list", status = 400)
        else:
            return HttpResponse("No user logged-in.", status = 201)

        if changeMade:
            current_user.profile.save()
            return HttpResponse("Profile updated", status = 201)
        else:
            return HttpResponse("No change made - check format", status = 400)


import requests

class GenerateProfilePicture(views.APIView):

    def get(self, request, *args, **kwards):

        for profile in Profile.objects.all():
            picurl = "https://picsum.photos/200/300/?random"
            r = requests.get(picurl).url
            profile.pic = r
            profile.save()


        return HttpResponse("gucci", status = 200)

          
class FrontendAppView(View):
    """
    Serves the compiled frontend entry point (only works if you have run `yarn
    run build`).
    """

    def get(self, request):
        try:
            with open(os.path.join('build', 'index.html')) as f:
                return HttpResponse(f.read())
        except FileNotFoundError:
            logging.exception('Production build of app not found')
            return HttpResponse(
                """
                This URL is only used when you have built the production
                version of the app. Visit http://localhost:3000/ instead, or
                run `yarn run build` to test the production version.
                """,
                status=501,
            )


class FindCuratorsView(views.APIView):

    # Given userID, return similar users. 

    def get(self, request, *args, **kwargs):
        current_user = request.user
        data = {}

        if current_user.is_authenticated:
            curators = SimilarUsers.find(current_user)
            data['curators'] = curators
            return HttpResponse(json.dumps(data), status = 200)
        else:
            return HttpResponse('Unauthorized user.', status = 401)


class RecommendMovieView(views.APIView):

    # Recommends movies to followers.
    # Input: user ids and movie id 

    def post(self, request, *arg, **kwargs):
        content = request.data
        
        try:
            imdbID = content['imdbID']
            profileID = content['profileID']
        except KeyError:
            return HttpResponse('Data not available.', status=400)

        if not Movie.objects.filter(imdbId=imdbID).exists():
            AddMovieToDB(imdbID)

        movie = Movie.objects.get(imdbId=imdbID)
            
        # Go through user IDs and add movieID to recommended_movies field
        for pid in profileID:
            profile = Profile.objects.get(id=pid)
            profile.recommended_movies.add(movie)

        return HttpResponse('Successfully added.', status=201)



# -------------------------------------------------- MOVIE VIEWS --------------------------------------------------------------#

class GetTopMoviesView(views.APIView):
    def get(self, request, *arg, **kwargs):

        ia = Imdb()

        #pass int argument between 1-100 to get a list
        #of the top movies right now
        numtop = 50
        top100 = ia.get_popular_movies()
        tosend = []

        index = 0

        for m in top100['ranks']:
            index = index + 1
            if index > int(numtop):
                break
            m_dict = {}
            imdbId =  m['id'][7:16]
            m_dict['imdbId'] = str(imdbId)
            m_dict['title'] = str(m['title'])
            m_dict['posterUrl'] = str(m['image']['url'])
            m_dict['year'] = str(m['year'])
            tosend.append(m_dict)

        try:
            return HttpResponse(json.dumps(tosend))
        except ValueError:
            return HttpResponse("ValueError, int between 1-100 plz", status = 400)


class SearchMoviesView(views.APIView):
    def post(self, request, *arg, **kwargs):
        ia = Imdb()

        query = request.data['query']

        searchResult = ia.search_for_title(query)
        tosend = []

        for m in searchResult:
            imdbId = m['imdb_id']
            if imdbId[0:2] == 'tt':
                m_dict = {}
                m_dict['imdbId'] = imdbId
                m_dict['title'] = m['title']
                m_dict['year'] = str(m['year'])
                # m_dict['posterUrl'] = ia.get_title(imdbId)['base']['image']['url']
                tosend.append(m_dict)


        return HttpResponse(json.dumps(tosend))

class MoviesView(views.APIView):
    """
    This view responds with json file containing movie data based on request
    """
    
    def post(self, request, *arg, **kwargs ):
        content = request.data
        ia = Imdb()

        try:
            #pass in imdb movie id to get movie details
            data = content['movieId']
            try:
                movie = ia.get_title(data)
                return HttpResponse(json.dumps(movie))
            except ValueError:
                return HttpResponse("Invalid IMDB id", status = 400)
        except KeyError:
            pass




        try:
            #pass int argument between 1-100 to get a list
            #of the top movies right now
            numtop = content['top']
            top100 = ia.get_popular_movies()
            tosend = []

            index = 0

            for m in top100['ranks']:
                index = index + 1
                if index > int(numtop):
                    break
                m_dict = {}
                imdbId =  m['id'][7:16]
                m_dict['imdbId'] = str(imdbId)
                m_dict['title'] = str(m['title'])
                m_dict['posterUrl'] = str(m['image']['url'])
                m_dict['year'] = str(m['year'])
                tosend.append(m_dict)
    
            try:
                return HttpResponse(json.dumps(tosend))
            except ValueError:
                return HttpResponse("ValueError, int between 1-100 plz", status = 400)
        except KeyError:
            pass


        try:
            #pass imdb id to get a list of similar titles
            data = content['similar']
            try:
                similarTitles = ia.get_title_similarities(data)
                return HttpResponse(json.dumps(similarTitles))
            except ValueError:
                return HttpResponse("Invalid IMDB id", status = 400)
        except KeyError:
            return HttpResponse('Request Not Understood.', status = 400)


#------------------------------Helper Functions-----------------------------#

"""
Adds a movie to the database, raises a ValueError exception
if the imdbId of the title given does not exist

raise exception of the movie is already in the db
"""
def AddMovieToDB(imdbId):
    ia = Imdb()
    data = ia.get_title(imdbId)
    title = data['base']['title']
    imageUrl = data['base']['image']['url']
    genres = ia.get_title_genres(imdbId)['genres']
    year = data['base']['year']

    movie = Movie(imdbId = imdbId, year = year, poster = imageUrl, genre = genres, title = title)

    movie.save()

    return


"""
A view I used to generate profile cuz I am lazy to learn
how to automate sending requests to a node
"""

"""
import names
import random

class GenerateProfile(views.APIView):

    def post(self, request, *args, **kwards):
        ia = Imdb()
        top100 = ia.get_popular_movies()['ranks']
        numInitialMoview = 50
        numProfiles = 700

        for x in range(numProfiles):
            firstName = names.get_first_name()
            lastName = names.get_last_name()
            email = firstName + lastName + '@fake.com'
            username = firstName
            password = lastName

            #create the user
            try:
                user = User.objects.create_user(username)
                user.set_password(password)
                user.email = email
                user.first_name = firstName
                user.last_name = lastName
                user.save()
                user.profile.fake = True
                user.profile.bio = firstName
                user.profile.save()
            except IntegrityError:
                pass

            #generate a random, yet meaningfull list of movies
            numMovies = random.randint(5,40)
            randInt = random.randint(1,100)
            toAdd = top100[randInt]['id'][7:16]

            for i in  range(numMovies):
                try:
                    if Movie.objects.filter(imdbId = toAdd).exists():
                        pass
                    else:
                        AddMovieToDB(toAdd)
                    movieObject = Movie.objects.get(imdbId = toAdd)
                    user.profile.movies.add(movieObject)
                    user.profile.save()
                except KeyError:
                    pass
                except IntegrityError:
                    return HttpResponse("Hmm Something went wrong", status = 400)
                except UnboundLocalError:
                    pass
                try:
                    toAdd = ia.get_title_similarities(toAdd)['similarities']
                    try:
                        randInt = random.randint(1,5)
                        toAdd = toAdd[randInt]['id'][7:16]
                    except IndexError:
                        pass
                except ValueError:
                    return HttpResponse(str(toAdd))
        
"""